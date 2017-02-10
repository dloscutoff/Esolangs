
(load utilities)
(load lists)

(def apply
  (lambda
    (func arglist)
    (eval (cons (q func) (quote-each arglist)))))

(def map
  (lambda
    (func ls)
    (if ls
      (cons
        (apply func (list (head ls)))
        (map func (tail ls)))
      nil)))

(def _foldl
  (lambda
    (func accum ls)
    (if ls
      (_foldl func
        (apply func (list accum (head ls)))
        (tail ls))
      accum)))

(def foldl-default
  (lambda
    (func ls default)
    (if ls
      (_foldl func (head ls) (tail ls))
      default)))

(def foldl (lambda (func ls) (foldl-default func ls nil)))

(def _chain-last
  (macro
    args
    (if (nil? (tail args))
      (list (q (arg)) (head args))
      (eval
        (cons
          (q _chain-last)
          (cons
            (insert-end (head args) (htail args))
            (ttail args)))))))

(def chain-last
  (macro
    args
    (eval
      (cons
        (q _chain-last)
        (cons
          (insert-end (q arg) (head args))
          (tail args)))))))
