
(load utilities)
(load lists)

(def single-char
  (lambda (charcode)
    (string (list charcode))))

(def spc (single-char 32))
(def nl (single-char 10))

(def strlen
  (lambda (str)
    (length (chars str))))

(def strcat
  (lambda (str1 str2)
    (string
      (concat (chars str1) (chars str2)))))

(comment This function can also be used on lists)
(def starts-with?
  (lambda (str prefix)
    (if (equal? (type str) Name)
      (starts-with? (chars str) (chars prefix))
      (if prefix
        (if str
          (if (equal? (head str) (head prefix))
            (starts-with? (tail str) (tail prefix))
            0)
          0)
        1))))

(def join2
  (lambda (str1 str2 sep)
    (strcat str1 (strcat sep str2))))

(def join
  (lambda (strlist sep)
    (foldl-default
      (substitute
        (q _sep)
        (quote sep)
        (lambda (str1 str2)
          (join2 str1 str2 _sep)))
      strlist
      (string nil))))
