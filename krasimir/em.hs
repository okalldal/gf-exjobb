import PGF2
import qualified Data.Map.Strict as Map
import Data.List(nub,foldl')
import Data.Maybe(fromMaybe)
import Debug.Trace

main = do
  gr <- readPGF "Dictionary.pgf"

  let Just eng = Map.lookup "DictionaryEng" (languages gr)
  en_cs <- readCounts eng "en.txt"

  let Just bul = Map.lookup "DictionaryBul" (languages gr)  
  bg_cs <- readCounts bul "bg.txt"

  let Just swe = Map.lookup "DictionarySwe" (languages gr)  
  sv_cs <- readCounts swe "sv.txt"

  let cs = en_cs ++ bg_cs ++ sv_cs
  print (length cs)

  let ps = mkProbs gr (Map.toList (iter 100 Map.empty cs))
  writeFile "probs.txt" (unlines [f++"\t"++show p | (f,p) <- ps])

readCounts :: Concr -> FilePath -> IO [([Fun],Int)]
readCounts concr fpath = fmap (concatMap toEntry . lines) $ readFile fpath
  where
    toEntry l
      | null fs   = []
      | otherwise = [(fs,read w2::Int)]
      where [w1,w2] = words l
            fs = nub [f | (f,_,_) <- lookupMorpho concr w1]

mkProbs gr f_ps =
  let c_ps  = foldl' addCount Map.empty f_ps
      total = Map.foldl (+) 0 c_ps
  in map (toFunProb c_ps) f_ps ++ 
     map (toCatProb total) (Map.toList c_ps)
  where
    addCount c_ps (f,p) =
      let DTyp _ cat _ = functionType gr f
      in Map.insertWith (+) cat p c_ps
      
    toFunProb c_ps (f,p) =
      let DTyp _ cat _ = functionType gr f
          total        = fromMaybe 0 (Map.lookup cat c_ps)
      in (f,p/total)

    toCatProb total (cat,p) = (cat,p/total)

iter 0 cs xs = cs
iter n cs xs = iter (n-1) (step cs xs) xs
  where
    step cs = foldl' (em cs) Map.empty

em :: Map.Map Fun Double -> Map.Map Fun Double -> ([Fun],Int) -> Map.Map Fun Double
em ps0 cs (fs,c) = foldl' addCount cs f_ps
  where
    f_ps  = [(f,getProb f) | f <- fs]
    total = sum (map snd f_ps)

    addCount cs (f,p) =
      Map.insertWith (+) f ((p/total)*fromIntegral c) cs

    getProb f = fromMaybe 1 (Map.lookup f ps0)

divergence qs ps =
  sum [p*log(p/q) | (f1,p) <- ps, (f2,q) <- qs, f1==f2]
