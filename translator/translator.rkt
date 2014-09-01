#lang racket

(define primitive #hash((+ . add) (- . sub) (* . mul) (/ . div) (True . True) (False . False)  
                        (data . data) (None . None) (unquote . unquote) (list . list) (zip . zip)
                        (< . less_than) (<= . less_equal) (= . equal) (>= . greater_equal) (> . greater)
                        (cond . cond) (else . otherwise) (and . logical_and) (or . logical_or)
                        (eval . eval) (update . update) (dict . dict) (str . str) (** . expand)
                        (apply . apply) (dot . dot) (in . pysay_in) (begin . begin)
                        (sum . sum) (max . max) (min . min) (index . index) (slice . slice) (len . len)
                        (define . define) (load . load) (dir . dir)
                        (file_to_string . file_to_string) (string_to_file . string_to_file)
                        (machine . machine) (connect . connect) (execute . execute) (vmstatus . vmstatus)
                        (display . display) (sleep . sleep) (listdir . listdir) (basename . basename)
                        (usandbox . usandbox) (datetime . datetime)))




(define (process-string str)
  (cond 
    ((regexp-match "!~{(.*?)}~" str)
     (process-string
      (regexp-replace "!~{(.*?)}~" str 
                      (lambda (all one) 
                        (let ((output (eval (read (open-input-string one))))
                              (outstr (open-output-string)))
                          (begin 
                            (parameterize ([current-output-port outstr])
                              (display output))
                            (string-append "\"\"" (get-output-string outstr) "\"\"")))))))
    ((regexp-match "~{(.*?)}~" str)
     (process-string
      (regexp-replace "~{(.*?)}~" str 
                      (lambda (all one) 
                        (let ((output (eval (read (open-input-string one))))
                              (outstr (open-output-string)))
                          (if (string? output)
                              (string-append "~(" output ")~")
                              (begin 
                                (parameterize ([current-output-port outstr])
                                  (display output))
                                (string-append "~(" (get-output-string outstr) ")~"))))))))
    (else str)))

(define (eval exp)
  (match exp
    ['lambda 'Lambda]
    [(? (lambda (e) (dict-has-key? primitive e))) (dict-ref primitive exp)]
    [(? symbol?) (string-append "'_pysayvm_" (symbol->string exp) "'")]
    [(? string?) (string-append "\"" (process-string exp) "\"")]
    [`(,f . ,args) (cons (eval f) (cons "," (eval args)))]
    [ _ exp]))

;; ======== Driver loop for I/O ========
(define output-end "#eos")
(define (driver-loop)
  (let ((input (read)))
    (if (not (eof-object? input))
        (let ((output (eval input)))
          (user-print output)
          (announce-output output-end)
          (driver-loop))
        (say-good-bye))))
(define (announce-output string)
  (newline)(display string)(newline))
(define (user-print object) (display object))
(define (say-good-bye) (newline))
;; ======== Start the evaluator ==========
(driver-loop)

