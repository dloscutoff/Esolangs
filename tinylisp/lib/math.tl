
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

(def _powers-of-2
  (lambda (num 2^i accum)
    (if (less? num 2^i)
      accum
      (_powers-of-2 num (add2 2^i 2^i) (cons 2^i accum)))))

(comment Helper function for binary multiplication: returns a list of powers of 2 that are <= given number)
(def powers-of-2
  (lambda (num) (_powers-of-2 num 1 nil)))

(def _mul2-binary
  (lambda (num reps binary-places accum)
    (if binary-places
      (if (less? reps (head binary-places))
        (_mul2-binary num reps (tail binary-places) (add2 accum accum))
        (_mul2-binary num
          (sub2 reps (head binary-places))
          (tail binary-places)
          (add2 (add2 accum accum) num)))
      accum)))

(def mul2
  (lambda (factor1 factor2)
    (if (less? (abs factor1) (abs factor2))
      (mul2 factor2 factor1)
      (if (negative? factor2)
        (_mul2-binary (neg factor1) (neg factor2) (powers-of-2 (neg factor2)) 0)
        (_mul2-binary factor1 factor2 (powers-of-2 factor2) 0)))))

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

(def _divides?
  (lambda (divisor multiple)
    (if (less? multiple divisor)
      (equal? multiple 0)
      (_divides? divisor (sub2 multiple divisor)))))

(def divides?
  (lambda (divisor multiple)
    (if divisor
      (if (negative? divisor)
        (divides? (neg divisor) multiple)
        (if (negative? multiple)
          (_divides? divisor (neg multiple))
          (_divides? divisor multiple)))
      0)))

(def even?
  (lambda (num) (_divides? 2 num)))

(def odd?
  (lambda (num)
    (not (_divides? 2 num))))

(comment When given a negative exponent, pow returns 0, except with special cases for bases 1, -1, or 0)
(comment When the exponent is 0, pow returns 1, even when the base is 0)
(def pow
  (lambda (base exponent)
    (if (negative? exponent)
      (if base
        (if (equal? (abs base) 1)
          (pow base (neg exponent))
          0)
        nil)
      (product (repeat-val base exponent)))))

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

(def _to-base
  (lambda (base num accum)
    (if (positive? num)
      (_to-base base
        (div2 num base)
        (cons (mod num base) accum))
      accum)))

(def to-base
  (lambda (base num)
    (if (positive? base)
      (if (equal? base 1)
        (repeat-val 1 num)
        (_to-base base num nil))
      nil)))

(def _from-base
  (lambda (base digits accum)
    (if digits
      (_from-base base
        (tail digits)
        (add2 (head digits) (mul2 accum base)))
      accum)))

(def from-base
  (lambda (base digits) (_from-base base digits 0)))

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
    (if (greater? test-factor num)
      accum
      (if (divides? test-factor num)
        (_prime-factors (div2 num test-factor) test-factor (cons test-factor accum))
        (_prime-factors num (inc test-factor) accum)))))

(comment Definition for 0 and negative numbers is chosen such that (product (prime-factors n)) equals n)
(def prime-factors
  (lambda (num)
    (if num
      (if (negative? num)
        (_prime-factors (neg num) 2 (list (neg 1)))
        (_prime-factors num 2 nil))
      (list 0))))
