
(load utilities)
(load metafunctions)
(load lists)

(def neg (lambda (n) (sub2 0 n)))

(def dec (lambda (n) (sub2 n 1)))

(def inc (lambda (n) (add2 1 n)))

(def -
  (lambda
    args
    (i args
      (i (tail args)
        (_foldl sub2 (head args) (tail args))
        (neg (head args)))
      0)))

(def +
  (lambda
    args
    (_foldl add2 (head args) (tail args))))

(def _mul2
  (lambda
    (val reps accum)
    (i reps
      (_mul2 val (dec reps) (add2 accum val))
      accum)))

(def mul2
  (lambda
    (arg1 arg2)
    (i (less? arg2 0)
      (_mul2 (neg arg1) (neg arg2) 0)
      (_mul2 arg1 arg2 0))))

(def * (lambda args (foldl-default mul2 args 1)))

(def _div2
  (lambda
    (dividend divisor quotient)
    (i (less? dividend divisor)
      quotient
      (_div2 (sub2 dividend divisor) divisor (inc quotient)))))

(def div2
  (lambda
    (arg1 arg2)
    (i arg2
      (i (less? arg2 0)
        (_div2 (neg arg1) (neg arg2) 0)
        (_div2 arg1 arg2 0))
      nil)))

(def /
  (lambda
    args
    (i args
      (i (tail args)
        (_foldl div2 (head args) (tail args))
        (div2 1 (head args)))
      1)))

(def mod
  (lambda
    (arg1 arg2)
    (i arg2
      (i (less? arg2 0)
        (neg (mod (neg arg1) (neg arg2)))
        (i (less? arg1 arg2)
          arg1
          (mod (sub2 arg1 arg2) arg2)))
      nil)))

(def even?
  (lambda
    (num)
    (i (less? num 0)
      (even? (neg num))
      (i (less? num 2)
        (zero? num)
        (even? (sub2 num 2))))))

(def odd?
  (lambda
    (num)
    (i (less? num 0)
      (odd? (neg num))
      (i (less? num 2)
        (equal? num 1)
        (odd? (sub2 num 2))))))

(def factorial (lambda (num) (apply * (1to num))))
