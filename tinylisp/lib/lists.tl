
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
    (if (equal? (type index) Int)
      (if (less? index 0)
        nil
        (if index
          (nth (tail ls) (sub2 index 1))
          (head ls)))
      nil)))

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
      (_insert
        val
        (cons (head ls-back) ls-front)
        (tail ls-back)
        (sub2 index 1))
      (_reverse
        ls-front
        (cons val ls-back)))))

(def insert
  (lambda
    (val ls index)
    (if (equal? (type index) Int)
      (if (less? index 0)
        nil
        (_insert val nil ls index))
      nil)))

(def insert-end
  (lambda
    (val ls)
    (reverse (cons val (reverse ls)))))

(def _quote-each
  (lambda
    (ls accum)
    (if ls
      (_quote-each
        (tail ls)
        (cons (list (q q) (head ls)) accum))
      (reverse accum))))

(def quote-each (lambda (ls) (_quote-each ls nil)))

(def _substitute
  (lambda
    (name value ls accum)
    (if ls
      (_substitute
        name
        value
        (tail ls)
        (cons (substitute name value (head ls)) accum))
      (reverse accum))))

(def substitute
  (lambda
    (name value original)
     (if (equal? (type original) List)
       (if (equal? (head original) (q q))
         original
         (_substitute name value original nil))
      (if (equal? original name)
        value
        original))))

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
    (if (nil? (tail args))
      (_inclusive-range nil 0 (sub2 (head args) 1))
      (_inclusive-range nil (head args) (sub2 (htail args) 1)))))
