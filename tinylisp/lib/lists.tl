
(load utilities)

(def _length
  (lambda
    (ls accum)
    (if ls
      (_length (tail ls) (add2 1 accum))
      accum)))

(def length (lambda (ls) (_length ls 0)))

(def nth
  (lambda
    (ls index)
    (if index
      (nth (tail ls) (sub2 index 1))
      (head ls))))

(def _reverse
  (lambda
    (ls accum)
    (if ls
      (_reverse (tail ls) (cons (head ls) accum))
      accum)))

(def reverse (lambda (ls) (_reverse ls nil)))

(def concat
  (lambda
    (ls-front ls-back)
    (_reverse (reverse ls-front) ls-back)))

(def _insert
  (lambda
    (val ls-front ls-back index)
    (if index
      (_insert val (cons (head ls-back) ls-front) (tail ls-back) (sub2 index 1))
      (_reverse ls-front (cons val ls-back)))))

(def insert
  (lambda
    (val ls index)
    (_insert val nil ls index)))

(def insert-end
  (lambda
    (val ls)
    (reverse (cons val (reverse ls)))))

(def _inclusive-range
  (lambda
    (accum lower upper)
    (if (less? upper lower)
       accum
       (_inclusive-range (cons upper accum) lower (sub2 upper 1)))))

(def inclusive-range
  (lambda
    (lower upper)
    (_inclusive-range nil lower upper)))

(def 1to
  (lambda (num)
    (_inclusive-range nil 1 num)))

(def range
  (lambda
    args
    (if (tail args)
      (_inclusive-range nil (head args) (sub2 (htail args) 1))
      (_inclusive-range nil 0 (sub2 (head args) 1)))))

(def quote-each
  (lambda
    (ls)
    (if ls
      (cons
        (list (q q) (head ls))
        (quote-each (tail ls)))
      nil)))
