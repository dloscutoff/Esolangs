
(load long-names)

(def Int (q Int))
(def List (q List))
(def Name (q Name))
(def Builtin (q Builtin))

(def list (q (args args)))

(def macro
  (q (nil
    (params expr)
    (cons nil (list params expr)))))

(def lambda (macro (params expr) (list params expr)))

(def comment (macro words nil))

(def nil? (lambda (val) (equal? val nil)))
(def zero? (lambda (val) (equal? val 0)))

(def cddr (lambda (ls) (cdr (cdr ls))))

(def cadr (lambda (ls) (car (cdr ls))))

(def _and
  (lambda
    (ls)
    (i ls
      (i (eval (head ls))
        (_and (tail ls))
        0)
      1)))

(def and (macro args (_and args)))

(def _or
  (lambda
    (ls)
    (i ls
      (i (eval (head ls))
        1
        (_or (tail ls)))
      0)))

(def or (macro args (_or args)))

(def not (lambda (val) (i val 0 1)))

