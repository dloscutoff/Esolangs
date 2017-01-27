(load utilities)

(def quote-each
  (lambda
    (ls)
    (i ls
      (cons
        (list (q q) (head ls))
        (quote-each (tail ls)))
      nil)))

(def apply
  (lambda
    (func arglist)
    (eval (cons (q func) (quote-each arglist)))))

(def map
  (lambda
    (func ls)
    (i ls
      (cons
        (apply func (list (head ls)))
        (map func (tail ls)))
      nil)))

(def _foldl
  (lambda
    (func accum ls)
    (i ls
      (_foldl func
        (apply func (list accum (head ls)))
        (tail ls))
      accum)))

(def foldl-default
  (lambda
    (func ls default)
    (i ls
      (_foldl func (head ls) (tail ls))
      default)))

(def foldl (lambda (func ls) (foldl-default func ls nil)))

(def _chain-left
  (lambda
    args
    (i (equals () (tail args)) (cons (quote (arg)) (cons (head args) ()))
      (eval (cons (quote _chain-left) (cons (append (head args) (head (tail args))) (tail (tail args))))))))

(def chain-left
  (lambda
    args
    (eval (cons (quote _chain-left) (cons (append (quote arg) (head args)) (tail args))))))

