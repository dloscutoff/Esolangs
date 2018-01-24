
(load utilities)
(load lists)
(load metafunctions)
(load math)

(def _transpose
  (lambda (matrix accum)
    (if (all matrix)
      (_transpose
        (map tail matrix)
        (cons (map head matrix) accum))
      (reverse accum))))

(def transpose
  (lambda (matrix)
    (if matrix (_transpose matrix nil) nil)))

(def zip
  (lambda args (transpose args)))

(def _each-head-or-default
  (lambda (matrix default accum)
    (if matrix
      (if (head matrix)
        (_each-head-or-default
          (tail matrix)
          default
          (cons (head (head matrix)) accum))
        (_each-head-or-default
          (tail matrix)
          default
          (cons default accum)))
      (reverse accum))))

(def _transpose-default
  (lambda (matrix default accum)
    (if (any matrix)
      (_transpose-default
        (map tail matrix)
        default
        (cons (_each-head-or-default matrix default nil) accum))
      (reverse accum))))

(def transpose-default
  (lambda (matrix default)
    (if matrix (_transpose-default matrix default nil) nil)))

(def _map*
  (lambda (func lists accum)
    (if lists
      (_map* func
        (tail lists)
        (cons (apply func (head lists)) accum))
      (reverse accum))))

(comment Takes a function and any number of lists and applies the function to corresponding elements of the lists)
(def map*
  (lambda func-and-lists
    (_map*
      (head func-and-lists)
      (transpose (tail func-and-lists))
      nil)))

