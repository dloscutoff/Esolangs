
(load utilities)
(load metafunctions)
(load lists)

(def abs
  (lambda (num)
    (if (negative? num)
      (neg num)
      num)))

(def -
  (lambda args
    (if args
      (if (tail args)
        (_foldl sub2 (head args) (tail args))
        (neg (head args)))
      0)))

(def +
  (lambda args (foldl-default add2 args 0)))

(def sum
  (lambda (ls) (foldl-default add2 ls 0)))

(def _mul2
  (lambda (val reps accum)
    (if reps
      (_mul2 val (dec reps) (add2 accum val))
      accum)))

(def mul2
  (lambda (factor1 factor2)
    (if (less? (abs factor1) (abs factor2))
      (mul2 factor2 factor1)
      (if (negative? factor2)
        (_mul2 (neg factor1) (neg factor2) 0)
        (_mul2 factor1 factor2 0)))))

(def *
  (lambda args (foldl-default mul2 args 1)))

(def product
  (lambda (ls) (foldl-default mul2 ls 1)))

(def _div2-positive
  (lambda (dividend divisor quotient)
    (if (less? dividend divisor)
      quotient
      (_div2-positive (sub2 dividend divisor) divisor (inc quotient)))))

(def _div2-negative
  (lambda (dividend divisor quotient)
    (if (negative? dividend)
      (_div2-negative (add2 dividend divisor) divisor (dec quotient))
      quotient)))

(def div2
  (lambda (dividend divisor)
    (if divisor
      (if (negative? divisor)
        (div2 (neg dividend) (neg divisor))
        (if (negative? dividend)
          (_div2-negative dividend divisor 0)
          (_div2-positive dividend divisor 0)))
      nil)))

(def /
  (lambda args
    (if args
      (if (tail args)
        (_foldl div2 (head args) (tail args))
        (div2 1 (head args)))
      1)))

(def _mod-positive
  (lambda (num modulus)
    (if (less? num modulus)
      num
      (_mod-positive (sub2 num modulus) modulus))))

(def _mod-negative
  (lambda (num modulus)
    (if (negative? num)
      (_mod-negative (add2 num modulus) modulus)
      num)))

(def mod
  (lambda (num modulus)
    (if modulus
      (if (positive? modulus)
        (if (negative? num)
          (_mod-negative num modulus)
          (_mod-positive num modulus))
        (neg (mod (neg num) (neg modulus))))
      nil)))

(def divides?
  (lambda (divisor multiple)
    (if (negative? divisor)
      (divides? (neg divisor) multiple)
      (if (negative? multiple)
        (divides? divisor (neg multiple))
        (if (less? multiple divisor)
          (zero? multiple)
          (divides? divisor (sub2 multiple divisor)))))))

(def even?
  (lambda (num) (divides? 2 num)))

(def odd?
  (lambda (num)
    (not (divides? 2 num))))

(def pow
  (lambda (base exponent)
    (product (repeat-val base exponent))))

(def _gcd-nonnegative
  (lambda (num1 num2)
    (if (less? num2 num1)
      (_gcd-nonnegative num2 num1)
      (if num1
        (_gcd-nonnegative (sub2 num2 num1) num1)
        num2))))

(def gcd
  (lambda (num1 num2)
    (if (negative? num1)
      (gcd (neg num1) num2)
      (if (negative? num2)
        (_gcd-nonnegative num1 (neg num2))
        (_gcd-nonnegative num1 num2)))))

(def max2
  (lambda (value1 value2)
    (if (less? value1 value2)
      value2
      value1)))

(def max
  (lambda (ls) (foldl max2 ls)))

(def min2
  (lambda (value1 value2)
    (if (less? value1 value2)
      value1
      value2)))

(def min
  (lambda (ls) (foldl min2 ls)))

(def factorial
  (lambda (num)
    (foldl-default mul2 (1to num) 1)))

(def _prime?
  (lambda (num factor)
    (if (less? factor num)
      (if (divides? factor num)
        0
        (_prime? num (inc factor)))
      1)))

(def prime?
  (lambda (num)
    (if (equal? num (neg 1))
      1
      (if (less? num 2)
        0
        (_prime? num 2)))))

(def _prime-factors
  (lambda (num test-factor accum)
    (if (less? test-factor num)
      (if (divides? test-factor num)
        (_prime-factors (div2 num test-factor) test-factor (cons test-factor accum))
        (_prime-factors num (inc test-factor) accum))
      accum)))

(def prime-factors
  (lambda (num)
    (if num
      (if (negative? num)
        (_factor (neg num) 2 (list (neg 1)))
        (_factor num 2 nil))
      (list 0))))
