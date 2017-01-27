(load utilities)

(def _length
  (lambda
    (ls accum)
    (i ls
      (_length (tail ls) (add2 1 accum))
      accum)))

(def length (lambda (ls) (_length ls 0)))

(def _reverse
  (lambda
    (ls accum)
    (i ls
      (_reverse (tail ls) (cons (head ls) accum))
      accum)))

(def reverse (lambda (ls) (_reverse ls nil)))

(def _inclusive-range
  (lambda
    (accumulator lower upper)
    (i (less? upper lower)
       accumulator
       (_inclusive-range (cons upper accumulator) lower (sub2 upper 1)))))

(def 1to
  (lambda (num)
    (_inclusive-range nil 1 num)))
    
(d append
  (lambda
    (val list)
    (rev (c val (rev list)))))
