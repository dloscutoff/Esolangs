
(load utilities)
(load lists)

(def apply
  (lambda (func arglist)
    (eval
      (cons (q func) (quote-each arglist)))))

(def _map
  (lambda (func ls accum)
    (if ls
      (_map
        func
        (tail ls)
        (cons
          (apply func (list (head ls)))
          accum))
      (reverse accum))))

(def map
  (lambda (func ls) (_map func ls nil)))

(def _filter
  (lambda (func ls accum)
    (if ls
      (_filter
        func
        (tail ls)
        (if (apply func (list (head ls)))
          (cons (head ls) accum)
          accum))
      (reverse accum))))

(def filter
  (lambda (func ls) (_filter func ls nil)))

(def _take-while
  (lambda (func ls accum)
    (if
      (if ls (func (head ls)) nil)
      (_take-while
        func
        (tail ls)
        (cons (head ls) accum))
      (reverse accum))))

(def take-while
  (lambda (func ls) (_take-while func ls nil)))

(def _foldl
  (lambda (func accum ls)
    (if ls
      (_foldl func
        (apply func (list accum (head ls)))
        (tail ls))
      accum)))

(def foldl-default
  (lambda (func ls default)
    (if ls
      (_foldl func (head ls) (tail ls))
      default)))

(def foldl
  (lambda (func ls) (foldl-default func ls nil)))

(def _chain-last
  (macro args
    (if (tail args)
      (list (q (arg)) (head args))
      (eval
        (cons
          (q _chain-last)
          (cons
            (insert-end (head args) (htail args))
            (ttail args)))))))

(def chain-last
  (macro args
    (eval
      (cons
        (q _chain-last)
        (cons
          (insert-end (q arg) (head args))
          (tail args))))))

(comment Example use of substitute to emulate closures: returns a single-argument function that adds a number to its argument)
(def add-n
  (lambda (num)
    (substitute
      (q num)
      num
      (lambda (x) (add2 num x)))))
