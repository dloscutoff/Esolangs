
(load long-names)

(def Int (q Int))
(def List (q List))
(def Name (q Name))
(def Builtin (q Builtin))

(def list (q (args args)))

(def macro
  (q (()
    (params expr)
    (cons nil (list params expr)))))

(def lambda (macro (params expr) (list params expr)))

(def comment (macro words nil))

(def neg (lambda (num) (sub2 0 num)))
(def dec (lambda (num) (sub2 num 1)))
(def inc (lambda (num) (add2 1 num)))

(def nil? (lambda (val) (equal? val nil)))
(def zero? (lambda (val) (equal? val 0)))
(def greater? (lambda (num1 num2) (less? num2 num1)))
(def positive? (lambda (num) (less? 0 num)))
(def negative? (lambda (num) (less? num 0)))

(def cddr (lambda (ls) (cdr (cdr ls))))
(def cadr (lambda (ls) (car (cdr ls))))
(def ttail (lambda (ls) (tail (tail ls))))
(def htail (lambda (ls) (head (tail ls))))

(def not (lambda (val) (if val 0 1)))
