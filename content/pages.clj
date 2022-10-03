(ns ssgen.core
  (:require [clojure.java.shell]
            [selmer.filters]
            [selmer.parser]
            [selmer.util]
            [clojure.java.io]
            [clojure.tools.trace]
            [clj-html-compressor.core]))
            ;; [com.yahoo.platform.yui.compressor]
            

(selmer.filters/add-filter!
 :human-readable-date
 (fn [date]
   (let [sdf (new java.text.SimpleDateFormat "yyyy LLLL d")]
    (.setTimeZone sdf (java.util.TimeZone/getTimeZone "GMT"))
    (.format
     sdf
     date))))

(selmer.filters/add-filter!
 :get-year
 (fn [date]
   (.format
    (new java.text.SimpleDateFormat "yyyy")
    date)))

(selmer.filters/add-filter!
 :iso-date
 (fn [date]
   (.format
    (new java.text.SimpleDateFormat "yyyy-MM-dd")
    date)))

(selmer.filters/add-filter!
 :replaceDashWithUnder
 (fn [html-string]
   (clojure.string/replace html-string "-"  "_")))

(selmer.filters/add-filter!
 :html2text
 (fn [html-string]
   (clojure.string/replace html-string #"<.*?>" "")))

(selmer.filters/add-filter!
 :warn-if-longer-than
 (fn [string length]
   (if (<= (count string) (Integer/parseInt length))
     string
     (do
       (println "String is too long")
       (println string)
       (println length)
       string))))

(selmer.util/set-missing-value-formatter!
 (fn [tag context-map]
   (throw (Exception. (str tag " does not exist in " (str context-map))))))

(def data (load-file "content/data.clj"))

(def compress-html
  ;; clj-html-compressor.core/compress
  (fn [x] x))
  

(defn compress-css [x]
  ;; (let [src-file (java.io.File/createTempFile "str" ".css")
  ;;       dst-file (java.io.File/createTempFile "str" ".css")]
  ;; (do
  ;;   (spit x src-file)
  ;;   (com.yahoo.platform.yui.compressor/YUICompressor/Main
  ;;    [(str src-file)
  ;;     "--type"
  ;;     "css"
  ;;     "-o"
  ;;     (str dst-file)])
  ;;   (slurp dst-file)))
  x)
  

;; (defn convert [file1 file2 & options]
;;   (let [tmpdir (java.nio.file.Files/createTempDirectory nil)
;;         file2 (.toFile (.resolve tmpdir file2))]
;;     (apply clojure.java.shell/sh `("convert" ~@options (str (.resolve tmpdir file2))))
;;     (slurp file2)))

(defn favicon-set [favicon-svg-path]
  {"/favicon.svg" (slurp favicon-svg-path)})
                                        ;(clojure.java.io/file "/" "favicon-32x32.png") (convert favicon-svg-path "favicon.ico" "-resize" "32x32")
                                        ;(clojure.java.io/file "/" "favicon-192x192.png") (convert favicon-svg-path "favicon.ico" "-resize" "192x192")
                                        ; TODO[3]: fix this
   


(defn check-post [post]
  (map
   (fn [tag]
     (if (not (contains? post tag))
       (throw
        (ex-info
         "Post does not contain tag"
         {:post (:slug post) :tag (str tag)}))
       nil))
   [:slug :title :teaser :contents :image])
  post)

                                        ; TODO[2]: compress img to standardized ratios
(defn compress-img [img-path] (slurp img-path))

(merge

 {"/raw-text/main.css" (compress-css
                    (slurp "content/raw-text/main.css"))

  "/404.html" (compress-html
               (selmer.parser/render
                (slurp "content/templates/page.html.jinja")
                (:not-found-page data)))

  "/index.html" (compress-html
                 (selmer.parser/render
                  (slurp "content/templates/page.html.jinja")
                  (:front-page data)))}

 (apply
  hash-map
  (flatten
   (map
    (fn [file] [(clojure.string/join "/" (concat [""] (drop 1 (.toPath file))))
                (fn [_] file)])
    (filter
     (fn [file] (.isFile file))
     (file-seq (clojure.java.io/file "content" "raw-binary"))))))

 (favicon-set "content/raw-text/favicon.svg")

                                        ; blog index
 (let [path "/essays/index.html"]

   {path (compress-html
          (selmer.parser/render
           (slurp "content/templates/page.html.jinja")
           {:page (:blog-meta data)
            :path path
            :site (:site data)
            :content (selmer.parser/render
                      (slurp "content/templates/blog_index.html.jinja")
                      (assoc
                       (:blog-meta data)
                       :posts
                       (map
                               (fn [post]
                                 (let [post (check-post (merge (:post-defaults data) post))]
                                   post))
                               (:blog-posts data))
                       :path path))}))})

                                        ; blog posts
 (apply
  merge
  (map
   (fn [post]
     (let [post (check-post (merge (:post-defaults data) post))
           path (clojure.java.io/file
                 "/"
                 "essays"
                 (str (:slug post) ".html"))
           page-content (compress-html
                         (selmer.parser/render
                          (slurp "content/templates/page.html.jinja")
                          {:page post
                           :path path
                           :site (:site data)
                           :content (selmer.parser/render
                                     (slurp "content/templates/blog_post.html.jinja")
                                     (assoc post :path path))}))]
       {path page-content}))
   (:blog-posts data))))
