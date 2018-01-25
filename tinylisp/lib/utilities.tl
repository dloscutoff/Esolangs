
(load long-names)

(def Int (q Int))
(def List (q List))
(def Name (q Name))
(def Builtin (q Builtin))

(def list (q (args args)))

(def macro
  (q
   (() (params expr) (list nil params expr))))

(def lambda (macro (params expr) (list params expr)))

(def comment (macro words nil))

(def quote
  (lambda (expr)
    (list (q q) expr)))

(def neg (lambda (num) (sub2 0 num)))
(def dec (lambda (num) (sub2 num 1)))
(def inc (lambda (num) (add2 1 num)))

(def nil? (lambda (val) (equal? val nil)))
(def zero? (lambda (val) (equal? val 0)))
(def greater? (lambda (num1 num2) (less? num2 num1)))
(def positive? (lambda (num) (less? 0 num)))
(def negative? (lambda (num) (less? num 0)))

(def type?
  (lambda (val some-type) (equal? (type val) some-type)))

(def cadr (lambda (ls) (car (cdr ls))))
(def cddr (lambda (ls) (cdr (cdr ls))))
(def htail (lambda (ls) (head (tail ls))))
(def ttail (lambda (ls) (tail (tail ls))))

(def not (lambda (val) (if val 0 1)))

(def both
  (lambda (cond1 cond2)
    (if cond1
      (if cond2 1 0)
      0)))

(def either
  (lambda (cond1 cond2)
    (if cond1
      1
      (if cond2 1 0))))

(def neither
  (lambda (cond1 cond2)
    (if cond1
      0
      (if cond2 0 1))))
