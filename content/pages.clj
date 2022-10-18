(ns ssgen.core
  (:require [clojure.java.shell]
            [clj-yaml.core]
            [clojure.string]
            [clojure.java.io]
            [clojure.java.shell]
            [selmer.filters]
            [selmer.parser]
            [selmer.util]
            [clojure.tools.trace]
            [clj-html-compressor.core]))

(defn today [] (new java.util.Date))

(defn pandoc [document]
  (:out (clojure.java.shell/sh "pandoc" :in document :out-enc "UTF-8")))

(defn parse-yaml-markdown [path]
  (let [contents (clojure.string/split (slurp path) #"---" 3)]
    (merge
     (clj-yaml.core/parse-string (second contents))
     {:content (pandoc (get contents 2))
      :slug (first
             (clojure.string/split
              (.getName path)
              #"\."))})))

(def sam {:name "Samuel Grayson"
          :url "https://samgrayson.me"
          :twitter "charmonium"})

(def site {:name "Samuel Grayson"
           :twitter "charmoniumQ"
           :author sam
           :url "https://samgrayson.me"
           :cname "samgrayson.me"
           :root ""
           :favicon (clojure.java.io/file "content" "raw-text" "favicon.svg")
           :nav [{:url "https://scholar.google.com/citations?user=EEOIkYEAAAAJ&hl=en", :text "Publications"}
                 ;; {:url "/cv.html" :text "CV"}
                 {:url "/essays" :text "Essays"}]})

(defn post-url [post] (str "/essays/" (:slug post)))

(selmer.filters/add-filter! :post-url post-url)

(selmer.filters/add-filter!
 :human-readable-date
 #(let [sdf (new java.text.SimpleDateFormat "yyyy LLLL d")]
    (.setTimeZone sdf (java.util.TimeZone/getTimeZone "GMT"))
    (.format sdf %)))

(selmer.filters/add-filter!
 :get-year
 #(.format
   (new java.text.SimpleDateFormat "yyyy")
   %))

(selmer.filters/add-filter!
 :iso-date
 #(.format
   (new java.text.SimpleDateFormat "yyyy-MM-dd")
   %))

(selmer.filters/add-filter!
 :replaceDashWithUnder
 #(clojure.string/replace % "-"  "_"))

(selmer.filters/add-filter!
 :html2text
 #(clojure.string/replace % #"<.*?>" ""))

(selmer.filters/add-filter!
 :warn-if-longer-than
 (fn [string length]
   (if (> (count string) (Integer/parseInt length))
     (println (format "String is longer than %s: %s" length string)))
   string))

(selmer.util/set-missing-value-formatter!
 (fn [tag context-map]
   (throw
    (Exception.
     (str tag " does not exist in "
          (let [context-str (str context-map)
                limit 200]
            (if (> (count context-str) limit)
              (subs context-str 0 200)
              context-str)))))))

(defn compress-html [x] x)
                                        ; TODO[2]: use  clj-html-compressor.core/compress


;; (defn compress-css [x]
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
;; )


;; (defn convert [file1 file2 & options]
;;   (let [tmpdir (java.nio.file.Files/createTempDirectory nil)
;;         file2 (.toFile (.resolve tmpdir file2))]
;;     (apply clojure.java.shell/sh `("convert" ~@options (str (.resolve tmpdir file2))))
;;     (slurp file2)))

;; (defn favicon-set [favicon-svg-path]
;;   {"/favicon-32x32.png" (convert favicon-svg-path "favicon.ico" "-resize" "32x32"),
;;    "/favicon-192x192.png" (convert favicon-svg-path "favicon.ico" "-resize" "192x192")})
                                        ; TODO[3]: fix this

(def front-page
  {:content (slurp "content/front_page.html")
   :path "/"
   :page {:title "Samuel Grayson"
          :teaser "Samuel Grayson’s site"
          :content? true
          :language "en-US"
          :image {:url "/raw-binary/self.jpg"
                  :alt "Samuel Grayson"}}
   :site site})

(def blog-meta
  {:title "Essays"
   :teaser "Sam’s essays on computer science, math, history, language, and law."
   :author sam
   :image {:alt "A painting of The Nighthawks by Edward Hopper"
           :url "https://upload.wikimedia.org/wikipedia/commons/a/a8/Nighthawks_by_Edward_Hopper_1942.jpg"
           :caption "A cool picture"
           :attribution {:text "The Nighthawks by Edward Hopper (1942)"
                         :attrib_url "https://en.wikipedia.org/wiki/File:Nighthawks_by_Edward_Hopper_1942.jpg"}}
   :language "en-US"
   :content? true})

(def post-defaults
  {:license {:name "Creative Commons Attribution 4.0 International License"
             :url "http://creativecommons.org/licenses/by/4.0/"}
   :date-published (today)
   :date-modified nil
   :author sam
   :language "en-US"
   :content? true})

(def blog-posts
  (reverse
   (sort-by
    :date-published
    (map
     parse-yaml-markdown
     (filter
      #(.isFile %)
      (file-seq (clojure.java.io/file "content/posts")))))))

(defn check-post [post]
  (map
   #(if (not (contains? post %))
      (throw
       (ex-info
        "Post does not contain tag"
        {:post (:slug post) :tag (str %)}))
      nil)
   [:slug :title :teaser :contents :image])
  post)

                                        ; TODO[2]: compress img to standardized ratios
(defn compress-img [img-path] (slurp img-path))

(merge

 {"/404.html" (compress-html
               (selmer.parser/render
                (slurp "content/templates/page.html.jinja")
                {:content (slurp "content/404.html")
                  :page {:title "Page not found"
                         :content? false
                         :language "en-US"}
                  :site site}))

  "/index.html" (compress-html
                 (selmer.parser/render
                  (slurp "content/templates/page.html.jinja")
                  (merge
                   front-page
                   {:content (selmer.parser/render (:content front-page) {})})))}

  ;; "/CNAME" (:cname site)
  

 (apply
  hash-map
  (flatten
   (map
    (fn [file] [(clojure.string/join "/" (concat [""] (drop 1 (.toPath file))))
                (fn [_] file)])
    (filter
     #(.isFile %)
     (file-seq (clojure.java.io/file "content" "raw-text"))))))

 (apply
  hash-map
  (flatten
   (map
    (fn [file] [(clojure.string/join "/" (concat [""] (drop 1 (.toPath file))))
                (fn [_] file)])
    (filter
     #(.isFile %)
     (file-seq (clojure.java.io/file "content" "raw-binary"))))))


                                        ; blog index
 (let [path "/essays/index.html"]

   {path (compress-html
          (selmer.parser/render
           (slurp "content/templates/page.html.jinja")
           {:page blog-meta
            :path path
            :site site
            :content (selmer.parser/render
                      (slurp "content/templates/blog_index.html.jinja")
                      (assoc
                       blog-meta
                       :posts (map
                               #(check-post (merge post-defaults %))
                               blog-posts)
                       :path path))}))})

 (apply
  merge
  (map
   (fn [post]
     (apply
      merge
      (map
       (fn [other-route]
         {other-route
          (selmer.parser/render
           (slurp "content/templates/redirect.html.jinja")
           {:url (post-url post)})})
       (:other_routes post))))
   blog-posts))

                                        ; blog posts
 (apply
  merge
  (map
   (fn [post]
     (let [post (check-post (merge post-defaults post))
           path (str (post-url post) "/index.html")
           page-content (compress-html
                         (selmer.parser/render
                          (slurp "content/templates/page.html.jinja")
                          {:page post
                           :path path
                           :site site
                           :content (selmer.parser/render
                                     (slurp "content/templates/blog_post.html.jinja")
                                     (assoc post :path path))}))]
       {path page-content}))
   blog-posts)))
