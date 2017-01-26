(load long-names)

(def last
  (q (
    (list)
    (i (equals? nil (tail list)) (car list)
      (last (tail list))))))

(d _rev
  (q (
    (orig new)
    (i (equals? nil (tail orig)) (cons (car orig) new)
      (_rev (tail orig) (cons (car orig) new))))))

(d rev
  (q (
    (list)
    (_rev list ()))))

(d append
  (q (
    (val list)
    (rev (cons val (rev list))))))
