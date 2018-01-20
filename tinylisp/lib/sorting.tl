
(load utilities)
(load lists)
(load metafunctions)

(def _insertion-sort
  (lambda (ls accum)
    (if ls
      (_insertion-sort
        (tail ls)
        (_insert-in-sorted (head ls) accum nil))
      accum)))

(def _insert-in-sorted
  (lambda (elem ls accum)
    (if ls
      (if (less? (head ls) elem)
        (_insert-in-sorted elem
          (tail ls)
          (cons (head ls) accum))
        (_reverse accum (cons elem ls)))
      (_reverse accum (cons elem ls)))))

(def insertion-sort
  (lambda (ls) (_insertion-sort ls nil)))

(def _merge-sorted
  (lambda (accum ls1 ls2)
    (if ls1
      (if ls2
        (if (less? (head ls1) (head ls2))
          (_merge-sorted (cons (head ls1) accum) (tail ls1) ls2)
          (_merge-sorted (cons (head ls2) accum) ls1 (tail ls2)))
        (_reverse accum ls1))
      (_reverse accum ls2))))

(def _partition
  (lambda (main-ls ls1 ls2)
    (if main-ls
      (_partition (tail main-ls) ls2 (cons (head main-ls) ls1))
      (list ls1 ls2))))

(def merge-sort
  (lambda (ls)
    (if (tail ls)
      (apply _merge-sorted
        (cons nil
          (map
            merge-sort
            (_partition ls nil nil))))
      ls)))

(comment In progress: quicksort)

(def _partition-by-pivot
  (lambda (main-ls pivot smaller-ls greater-ls)
    (if main-ls
      (if (less? (head main-ls) pivot)
        (_partition-by-pivot
          (tail main-ls)
          pivot
          (cons (head main-ls) smaller-ls)
          greater-ls)
        (_partition-by-pivot
          (tail main-ls)
          pivot
          smaller-ls
          (cons (head main-ls) greater-ls)))
      (list smaller-ls greater-ls))))
