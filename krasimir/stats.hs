import GHC.IO.Encoding
import PGF2
import qualified Data.Map.Strict as Map
import qualified Data.Set as Set
import Data.List(foldl',sortBy)
import Control.Monad(liftM2)
import Data.Maybe(fromMaybe)
import Debug.Trace

main = do
  setLocaleEncoding utf8
  gr <- readPGF "Dictionary.pgf"
  let Just eng = Map.lookup "DictionaryEng" (languages gr)
  lss <- fmap (splitSentences eng . lines) $ readFile "UD_English/en-ud-dev.conllu"
  let en_unigrams = summarize (concat [concatMap toUnigram ls | ls <- lss])
  let en_bigrams  = summarize (concat [concatMap (toBigram ls) ls | ls <- lss])

  let Just bul = Map.lookup "DictionaryBul" (languages gr)
  lss <- fmap (splitSentences bul . lines) $ readFile "UD_Bulgarian/bg-ud-dev.conllu"
  let bg_unigrams = summarize (concat [concatMap toUnigram ls | ls <- lss])
  let bg_bigrams  = summarize (concat [concatMap (toBigram ls) ls | ls <- lss])

  let Just swe = Map.lookup "DictionarySwe" (languages gr)
  lss <- fmap (splitSentences swe . lines) $ readFile "UD_Swedish/sv-ud-dev.conllu"
  let sv_unigrams = summarize (concat [concatMap toUnigram ls | ls <- lss])
  let sv_bigrams  = summarize (concat [concatMap (toBigram ls) ls | ls <- lss])

  let unigrams = en_unigrams ++ bg_unigrams ++ sv_unigrams
  putStrLn ("Number of unigrams: "++show (length unigrams))

  let bigrams  = en_bigrams  ++ bg_bigrams  ++ sv_bigrams
  putStrLn ("Number of bigrams:  "++show (length bigrams))

  putStrLn "Computing unigrams"
  unigram_ps <- em unigrams
  writeFile "unigram.txt" (unlines [f++"\t"++show p | (f,p) <- mkUnigramProbs gr unigram_ps])

  putStrLn "Unigram divergencies"
  putStrLn ("en "++show (compareProb unigram_ps en_unigrams))
  putStrLn ("bg "++show (compareProb unigram_ps bg_unigrams))
  putStrLn ("sv "++show (compareProb unigram_ps sv_unigrams))

  putStrLn "Computing bigrams"
  bigram_ps  <- em bigrams
  writeFile "bigram.txt" (unlines [x ++ "\t" ++ y ++ "\t" ++ show p | ((x,y),p) <- mkBigramProbs bigram_ps])

splitSentences cnc []   = []
splitSentences cnc (l:ls)
  | take 1 l == "#" = splitSentences cnc ls
  | otherwise       = let (ls1,ls2) = break null ls
                      in map (morpho . tsv) (l:ls1) : 
                         case ls2 of
                           []    -> []
                           _:ls2 -> splitSentences cnc ls2
  where
    morpho fs =
      ((Set.toList . Set.fromList . map fst3 . lookupMorpho cnc) (fs !! 1)
      ,read (fs !! 6)
      )

    fst3 (x,y,z) = x

tsv :: String -> [String]
tsv "" = []
tsv cs =
  let (x,cs1) = break (=='\t') cs
  in x : if null cs1 then [] else tsv (tail cs1)

toUnigram :: ([Fun], Int) -> [([Fun], Double)]
toUnigram (ax,root)
  | null ax   = []
  | otherwise = [(ax, 1.0)]

toBigram :: [([Fun], Int)] -> ([Fun], Int) -> [([(Fun, Fun)], Double)]
toBigram ls (ax,root)
  | null ax || null ay = []
  | otherwise          = [(liftM2 (,) ax ay, 1.0)]
  where
    ay = if root == 0 then [] else fst (ls !! (root - 1))

summarize :: Ord k => [(k,Double)] -> [(k,Double)]
summarize = Map.toList . Map.fromListWith (+)

compareProb ps0 cs = divergency 1 ps ps'
  where
    ps  = Map.fromListWith (+) [(ids,c / total) | (ids,c) <- cs]
          where
            total = sum (map snd cs)
    ps' = Map.fromListWith (+) [(ids,c / total) | (ids,c) <- cs']
          where
            cs'   = [(ids,sum (map getCount ids)) | (ids,_) <- cs]
            total = sum (map snd cs')

    getCount f = fromMaybe 0 (Map.lookup f ps0)

--------------------------------------------------------------
-- This function takes the estimated counts for the functions
-- and computes the probabilities P(f | C) and P(C).
-- In the process it also does Laplace smoothing

mkUnigramProbs gr f_ps0 =
  let f_ps  = [(f,fromMaybe 0 (Map.lookup f f_ps0) + 1) | f <- functions gr]
      c_ps  = foldl' addCount Map.empty f_ps
      total = Map.foldl (+) 0 c_ps
  in map (toFunProb c_ps) f_ps ++
     map (toCatProb total) (Map.toList c_ps)
  where
    addCount c_ps (f,p) =
      let (_, cat, _) = unType $ functionType gr f
      in Map.insertWith (+) cat p c_ps

    toFunProb c_ps (f,p) =
      let (_, cat, _) = unType $ functionType gr f
          total        = fromMaybe 0 (Map.lookup cat c_ps)
      in (f,p/total)

    toCatProb total (cat,p) = (cat,p/total)

--------------------------------------------------------------
-- This function takes the estimated counts for the pairs 
-- of functions and computes the probabilities P(f1,f2).
-- There is no smoothing since these probabilities are expected
-- to be used together with a unigram back off. On the other hand
-- we take away very low probability events since those are just
-- artefacts from the roundings.

mkBigramProbs :: Map.Map k Double -> [(k,Double)]
mkBigramProbs cs =
  let (total,ps) = (clip total 0 . sortBy count) (Map.toList cs)
  in ps
  where
    count :: (k,Double) -> (k,Double) -> Ordering
    count (_,c1) (_,c2) = compare c2 c1

    total0     = Map.foldl (+) 0 cs :: Double
    max        = total0 * exp(-kl_limit) :: Double

    clip total sum ((x,p):xs)
      | sum < max             = let (sum',ys) = clip total (sum + p) xs
                                in (sum',(x,p/total) : ys)
    clip total sum _          = (sum,[])

------------------------------------------------------------
-- This function is the core of the algorithm. Here we use
-- expectation maximization to estimate the counts.
-- The first argument is a list of pairs. The first element
-- of every pair is the list of possible keys and the second
-- element is how many times we have seen this list of 
-- possibilities. The result is the estimated count for each
-- of the keys. The estimation continues until convergency, i.e.
-- until the KL divergency is less than kl_limit.

em :: Ord k => [([k],Double)] -> IO (Map.Map k Double)
em xs = loop 1 Map.empty xs
  where
    total = sum (map snd xs)

    -- k is [Fun] or [(Fun,Fun)], ps is map of probabilities, xs is data
    loop :: Int -> Map k Double -> [([k],Double)] -> IO (Map.Map k Double)
    loop n ps xs
      | abs kl < kl_limit = print (n,kl) >> return cs
      | otherwise         = print (n,kl) >> loop (n+1) cs xs
      where
        kl = divergency total cs ps
        --cs is new probabilities, here we iterate through all data points to update parameters
        cs = foldl' iter Map.empty xs

        --update count for all possible 'real' values of a data point
        --weighted by the probability of that being the real value, note that cs shadows the cs above
        iter cs (fs,c) = foldl' addCount cs f_ps
          where
            f_ps  = [(f,getProb f) | f <- fs]
            total = sum (map snd f_ps)

            addCount cs (f,p) =
              Map.insertWith (+) f ((p/total)*c) cs

        getProb f = fromMaybe 1 (Map.lookup f ps)

divergency total cs ps =
  foldl' (+) 0
      [p'*log(p'/p)/total | (f,p') <- Map.toList cs,
                            let p = fromMaybe 1 (Map.lookup f ps),
                            abs(p-p')/total > 1e-50]

kl_limit = 5e-8
