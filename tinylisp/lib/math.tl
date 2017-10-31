
(load utilities)
(load metafunctions)
(load lists)

(def neg (lambda (n) (sub2 0 n)))

(def dec (lambda (n) (sub2 n 1)))

(def inc (lambda (n) (add2 1 n)))

(def -
  (lambda args
    (if args
      (if (tail args)
        (_foldl sub2 (head args) (tail args))
        (neg (head args)))
      0)))

(def +
  (lambda args
    (_foldl add2 (head args) (tail args))))

(def _mul2
  (lambda (val reps accum)
    (if reps
      (_mul2 val (dec reps) (add2 accum val))
      accum)))

(def mul2
  (lambda (arg1 arg2)
    (if (less? arg2 0)
      (mul2 (neg arg1) (neg arg2))
      (if (less? arg1 0)
        (neg (mul2 (neg arg1) arg2))
        (if (less? arg1 arg2)
          (_mul2 arg2 arg1 0)
          (_mul2 arg1 arg2 0))))))

(def * (lambda args (foldl-default mul2 args 1)))

(def _div2
  (lambda (dividend divisor quotient)
    (if (less? dividend divisor)
      quotient
      (_div2 (sub2 dividend divisor) divisor (inc quotient)))))

(def div2
  (lambda (arg1 arg2)
    (if arg2
      (if (less? arg2 0)
        (_div2 (neg arg1) (neg arg2) 0)
        (_div2 arg1 arg2 0))
      nil)))

(def /
  (lambda args
    (if args
      (if (tail args)
        (_foldl div2 (head args) (tail args))
        (div2 1 (head args)))
      1)))

(def mod
  (lambda (arg1 arg2)
    (if arg2
      (if (less? arg2 0)
        (neg (mod (neg arg1) (neg arg2)))
        (if (less? arg1 arg2)
          arg1
          (mod (sub2 arg1 arg2) arg2)))
      nil)))

(def even?
  (lambda (num)
    (if (less? num 0)
      (even? (neg num))
      (if (less? num 2)
        (zero? num)
        (even? (sub2 num 2))))))

(def odd?
  (lambda (num)
    (if (less? num 0)
      (odd? (neg num))
      (if (less? num 2)
        (equal? num 1)
        (odd? (sub2 num 2))))))

(def max2
  (lambda (value1 value2)
    (if (less? value1 value2)
      value2
      value1)))

(def max (lambda (ls) (foldl max2 ls)))

(def min2
  (lambda (value1 value2)
    (if (less? value1 value2)
      value1
      value2)))

(def min (lambda (ls) (foldl min2 ls)))

(def factorial (lambda (num) (foldl-default mul2 (1to num) 1)))
