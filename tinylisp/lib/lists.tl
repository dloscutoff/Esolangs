
(load utilities)

(def _length
  (lambda (ls accum)
    (if ls
      (_length (tail ls) (add2 1 accum))
      accum)))

(def length
  (lambda (ls) (_length ls 0)))

(def nth
  (lambda (ls index)
    (if (equal? (type index) Int)
      (if (less? index 0)
        nil
        (if index
          (nth (tail ls) (sub2 index 1))
          (head ls)))
      nil)))

(def last
  (lambda (ls)
    (if ls
      (if (tail ls)
        (last (tail ls))
        (head ls))
      nil)))

(def _reverse
  (lambda (ls accum)
    (if ls
      (_reverse (tail ls) (cons (head ls) accum))
      accum)))

(def reverse
  (lambda (ls) (_reverse ls nil)))

(def concat
  (lambda (ls-front ls-back)
    (_reverse (reverse ls-front) ls-back)))

(def _insert
  (lambda (val ls-front ls-back index)
    (if index
      (_insert
        val
        (cons (head ls-back) ls-front)
        (tail ls-back)
        (sub2 index 1))
      (_reverse
        ls-front
        (cons val ls-back)))))

(def insert
  (lambda (val ls index)
    (if (equal? (type index) Int)
      (if (less? index 0)
        nil
        (_insert val nil ls index))
      nil)))

(def insert-end
  (lambda (val ls)
    (reverse (cons val (reverse ls)))))

(def contains?
  (lambda (ls item)
    (if ls
      (if (equal? (head ls) item)
        1
        (contains? (tail ls) item))
      0)))

(def _count-occurrences
  (lambda (ls item count)
    (if ls
      (if (equal? (head ls) item)
        (_count-occurrences (tail ls) item (inc count))
        (_count-occurrences (tail ls) item count))
      count)))

(def count-occurrences
  (lambda (ls item) (_count-occurrences ls item 0)))

(def _first-index
  (lambda (ls item index)
    (if ls
      (if (equal? (head ls) item)
        index
        (_first-index (tail ls) item (inc index)))
      nil)))

(def first-index
  (lambda (ls item) (_first-index ls item 0)))

(def _last-index
  (lambda (ls item index result-index)
    (if ls
      (if (equal? (head ls) item)
        (_last-index (tail ls) item (inc index) index)
        (_last-index (tail ls) item (inc index) result-index))
      result-index)))

(def last-index
  (lambda (ls item) (_last-index ls item 0 nil)))

(def _all-indices
  (lambda (ls item index accum)
    (if ls
      (if (equal? (head ls) item)
        (_all-indices (tail ls) item (inc index) (cons index accum))
        (_all-indices (tail ls) item (inc index) accum))
      (reverse accum))))

(def all-indices
  (lambda (ls item) (_all-indices ls item 0 nil)))

(def _quote-each
  (lambda (ls accum)
    (if ls
      (_quote-each
        (tail ls)
        (cons (list (q q) (head ls)) accum))
      (reverse accum))))

(def quote-each
  (lambda (ls) (_quote-each ls nil)))

(def _substitute
  (lambda (name val ls accum)
    (if ls
      (_substitute
        name
        val
        (tail ls)
        (cons (substitute name val (head ls)) accum))
      (reverse accum))))

(def substitute
  (lambda (name val original)
    (if (equal? (type original) List)
      (if (equal? (head original) (q q))
        original
        (_substitute name val original nil))
      (if (equal? original name)
        val
        original))))

(def _transpose
  (lambda (matrix accum)
    (if (all matrix)
      (_transpose
        (map tail matrix)
        (cons (map head matrix) accum))
      (reverse accum))))

(def transpose
  (lambda (matrix)
    (if matrix (_transpose matrix nil) nil)))

(def zip
  (lambda args (transpose args)))

(def _each-head-or-default
  (lambda (matrix default accum)
    (if matrix
      (if (head matrix)
        (_each-head-or-default
          (tail matrix)
          default
          (cons (head (head matrix)) accum))
        (_each-head-or-default
          (tail matrix)
          default
          (cons default accum)))
      (reverse accum))))

(def _transpose-default
  (lambda (matrix default accum)
    (if (any matrix)
      (_transpose-default
        (map tail matrix)
        default
        (cons (_each-head-or-default matrix default nil) accum))
      (reverse accum))))

(def transpose-default
  (lambda (matrix default)
    (if matrix (_transpose-default matrix default nil) nil)))

(def _inclusive-range
  (lambda (accum lower upper)
    (if (less? upper lower)
       accum
       (_inclusive-range (cons upper accum) lower (sub2 upper 1)))))

(def _reverse-inclusive-range
  (lambda (accum upper lower)
    (if (less? upper lower)
      accum
      (_reverse-inclusive-range (cons lower accum) upper (add2 lower 1)))))

(def inclusive-range
  (lambda (lower upper)
    (_inclusive-range nil lower upper)))

(def reverse-inclusive-range
  (lambda (upper lower)
    (_reverse-inclusive-range nil upper lower)))

(def 0to
  (lambda (num) (_inclusive-range nil 0 num)))

(def 1to
  (lambda (num) (_inclusive-range nil 1 num)))

(def to0
  (lambda (num) (_reverse-inclusive-range nil num 0)))

(def to1
  (lambda (num) (_reverse-inclusive-range nil num 1)))

(def range
  (lambda args
    (if (nil? (tail args))
      (_inclusive-range nil 0 (sub2 (head args) 1))
      (_inclusive-range nil (head args) (sub2 (htail args) 1)))))

(def _repeat-val
  (lambda (val count accum)
    (if count
      (_repeat-val val (dec count) (cons val accum))
      accum)))

(def repeat-val
  (lambda (val count) (_repeat-val val count nil)))

(def all
  (lambda (ls)
    (if ls
      (if (head ls)
        (all (tail ls))
        0)
      1)))

(def any
  (lambda (ls)
    (if ls
      (if (head ls)
        1
        (any (tail ls)))
      0)))
