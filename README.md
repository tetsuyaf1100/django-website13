# djangoチュートリアル #13

## 管理サイトをカスタマイズしよう！中編 〜モデル一覧設定編〜

djangoの大きな特徴の１つは自動生成された管理サイトがついてくることです。  
今回はモデル一覧画面をカスタマイズします。

## 完成版プロジェクト

<https://github.com/shun-rec/django-website-13>

## 事前準備

### 新規サーバーを立ち上げる

[Paiza](https://paiza.cloud)で作業している方はdjangoにチェックを入れて新規サーバーを立ち上げて下さい。  
自分のマシンで作業している方はdjangoが使える作業用フォルダを作成して下さい。

### 前回管理サイトをカスタマイズしたプロジェクトをダウンロード

ターミナルを開いて、以下を実行。

```sh
git clone https://github.com/shun-rec/django-website-12
```

フォルダを移動

```sh
cd django-website-07
```

### マイグレートしてDBを作成

```sh
python manage.py migrate
```

### スーパーユーザーを作成

```sh
python manage.py createsuperuser
```

* ユーザー名: admin
* メールアドレス: （無し）
* パスワード: admin

## モデル一覧にフィールドを表示しよう

ブログ一覧に「タイトル」「カテゴリ」「作成日」「更新日」を表示するようにしましょう。  
`ModelAdmin`のlist_display`を使用します。

`blog/admin.py`の`PostAdmin`に以下を追加します。

```py
    list_display = ('title', 'category', 'created', 'updated')
```

`ForeignKey`フィールド`OneToOne`フィールドの場合だけ注意が必要で、加えて`list_select_related`にも追加する必要があります。  
そうしないと、N+1問題というバグが発生します。  
ブログ一覧を取得するために1回DBにアクセスし、ブログがN件あるとすると、そのそれぞれのカテゴリを取得するためにさらにN回DBアクセスが発生します。  
これを1回のアクセスですべて取得する方法があります。  
ここでは`list_select_related`という仕組みを使用します。

※ N+1問題・・・DBアクセスが大量に発生し、サイトの負荷増大と速度低下を招く問題。

今回は`category`が`ForeignKey`フィールドなのでさらに以下を追加します。

```py
    list_select_related = ('category', )
```

### 動かしてみよう

開発サーバーを起動して管理サイトにアクセスしてみましょう。  

```sh
python manage.py runserver
```

ブログ一覧画面で「ID」「タイトル」「カテゴリ」「作成日」「更新日」カラムが表示されたらOKです。

## モデル一覧にManyToManyフィールド（多対多）を表示しよう

「タグ」カラムを表示してみましょう。

多対多のフィールドはそのままでは表示出来ません。  
今回は`tags`フィールドがその例です。  
複数あるタグをどのように表示するかを指示する必要があります。

今回はカンマ区切りで表示してみます。    
名前は既存のフィールド名と被らなければ何でも良いですが、`tags_summary`という名前でタグをカンマ区切りに整形するメソッドを定義します。

`blog/admin.py`の`PostAdmin`に続けて以下を追記します。

```py
    def tags_summary(self, obj):
        qs = obj.tags.all()
        label = ', '.join(map(str, qs))
        return label
```

カラム名を`tags`と変えてみましょう。  
`tags_summary`メソッドの下に（メソッドの外側）に以下を追記します。  
カラム名はこのように変更できます。

```py
    tags_summary.short_description = "tags"
```

これだけでもタグ一覧が表示されるようになりますが、この場合もN+1問題が発生しています。  
以下のメソッドをさらに追記して、N+1問題を回避しましょう。  
ManyToManyフィールドの場合には`prefetch_related`を使用します。  

```py
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('tags')
```

### 動かしてみよう

タグがカンマ区切りでリストに表示されていたらOKです。

## 一覧画面でモデルを編集出来るようにしよう

ブログ一覧画面で「タイトル」「カテゴリ」を修正出来るようにしてみましょう。  
「id」はもともと修正不可能で、「created」「updated」はモデルで修正不可と設定しました。  
`list_editable`にフィールド名をリストで指定します。

以下を`list_display`の下に追記しましょう。

```py
    list_editable = ('title', 'category')
```

### 動かしてみよう

ブログ一覧画面で複数のブログを一度に修正出来ればOKです。

## 検索出来るようにしよう。

ブログ一覧画面で「ID」「タイトル」「カテゴリ」「タグ」「作成日」「更新日」で検索出来るようにしてみましょう。

ForeignKeyやManyToManyフィールドではないフィールドは単純にフィールド名を`search_fields`のリストに追加するだけでOKです。  
ForeignKeyやManyToManyフィールドの場合には、そのフィールドを検索対象とするのかを追加で指示する必要があります。  
今回は`category`の`name`を検索するので、`category__name`と指示します。  
タグも同様に`tags__name`と指示します。

よって、`PostAdmin`の`list_editable`の下に以下を追記します。（順番は適当でOKです）

```py
    search_fields = ('title', 'category__name', 'tags__name', 'created', 'updated')
```

日付のフィールドの場合には、例えば2020年10月24日の場合には`2020-10-24`と検索出来るようになります。

検索でもN+1問題は発生しますが、先程対策したので大丈夫です。

### 動かしてみよう

ブログ一覧ページに検索窓が表示されるようになります。  
ここで各フィールドが検索出来るようになっていればOKです。

## デフォルトの並び替えを変更しよう

ブログ一覧を「更新日」が新しい順で並ぶようにしましょう。  
「更新日」が同じ場合は「作成日」が新しい順とします。

並び替えには`ordering`フィールドを使用します。  
デフォルトでは値が小さい順（古い順）に並ぶので`-`をつけることで反転させることが出来ます。

```py
    ordering = ('-updated', '-created')
```

### 動かしてみよう

ブログをいくつか追加して編集してみて、「更新日」「作成日」順に並んでいたらOKです。

## 絞り込み（フィルタ）機能を追加しよう

ブログサイトで「カテゴリごとのブログ一覧」や「過去1年間のブログ一覧」などの絞り込みを目にしたことがあると思います。  
それもdjangoの管理サイトではデフォルトで用意されています。  
「カテゴリ」「タグ」「作成日」「更新日」で絞り込みが出来るようにしましょう。  
`list_filter`フィールドを使用します。  

`ordering`の下に以下を追記します。

```py
    list_filter = ('category', 'tags', 'created', 'updated')
```

### 動かしてみよう

ブログ一覧ページに絞り込みのための右サイドバーが表示されたらOKです。

## カスタムフィルタを追加しよう

デフォルトで用意されているフィルタだけでなく、自作することも可能です。  
例えば、値段の範囲で商品を絞り込んだり。  
今回は本文に「ブログ」「開発」「日記」と含まれているブログを探すフィルタを追加してみます。  

カスタムフィルタを作成するには、`SimpleListFilter`を継承したクラスを作ります。  
そして、`title`、`parameter_name`、`queryset`、`lookups`の４つを定義します。

`blog/admin.py`の中の`PostAdmin`の上に以下のクラスを追加します。

```py
class PostTitleFilter(admin.SimpleListFilter):
    title = '本文'
    parameter_name = 'body_contains'

    def queryset(self, request, queryset):
        if self.value() is not None:
            return queryset.filter(body__icontains=self.value())
        return queryset

    def lookups(self, request, model_admin):
        return [
            ("ブログ", "「ブログ」を含む"),
            ("日記", "「日記」を含む"),
            ("開発", "「開発」を含む"),
        ]
```

* title フィルタの名前として表示されます
* parameter_name URLにつくパラメータの名前です。フィルタ結果をURLでシェアする時に便利です。
* queryset `self.value()`にユーザーが選択した値が入ってくるので、それで実際にフィルタします。
* lookups ユーザーに表示する選択肢のリストです。左が実際の値で、右が表示上のラベルです。

### 動かしてみよう

「本文」というフィルタが右サイドバーに表示されていたらOKです。

## モデルを一括で変更する独自のアクションを追加しよう

モデル一覧画面ではアクションと呼ばれる仕組みによって、チェックボックスでチェックしたモデルに一括で操作をすることが出来ます。  
例えば前回無効化した一括削除などです。  

今回はブログに「公開済み」「下書き」の状態を追加して、一括公開するアクションを追加してみましょう。

### Postモデルにpublishedフィールドを追加しよう

Postモデルに「公開済み」かどうかを表すpublishedというBooleanFieldを追加します。

`blog/models.py`の`Post`モデルの`tags`フィールドの下に以下を追加します。

```py
    published = models.BooleanField(default=True)
```

すでに公開済みのブログにも`published`フィールドが追加されるので`default=True`を指定しています。  
この`default`を指定しないと、次にDBに反映させる`migrate`を実行する時にエラーとなります。  
公開済みのブログについて`True`にするか`False`か、どうすればいいかdjangoが分からないからです。

### モデルの変更をDBに反映させます。

今回の本題からは外れますが、すでにDB上にあるモデルを変更したい時には、

1. マイグレーションファイルを作成
2. マイグレーションファイルをDBに適用

という順番で操作を行います。

コンソールで以下を順番に実行します。

```sh
python manage.py makemigrations
python manage.py migrate
```

### モデル一覧にpublishedフィールドを表示しよう

`list_display`に`published`を追加しましょう。

`blog/admin.py`の`PostAdmin`クラスを以下のように修正します。

```py
    list_display = ('id', 'title', 'category', 'tags_summary', 'published', 'created', 'updated')
```

### 一括で公開する・下書きに戻すアクションを追加しよう

それではいよいよアクションを追加しましょう。

独自のメソッドを追加して、それを`actions`フィールドにリストで指定します。

`blog/admin.py`の`PostAdmin`クラス内の下に以下を追記します。

```py
    actions = ["publish", "unpublish"]

    def publish(self, request, queryset):
        queryset.update(published=True)
        
    publish.short_description = "公開する"
        
    def unpublish(self, request, queryset):
        queryset.update(published=False)
        
    unpublish.short_description = "下書きに戻す"
```

### 動かしてみよう

ブログ一覧に２つのアクションが表示されて、チェックしたブログに適用されればOKです。

# djangoチュートリアル #14

## 管理サイトをカスタマイズしよう！後編 〜モデル個別設定編〜

djangoの大きな特徴の１つは自動生成された管理サイトがついてくることです。  
今回はモデル一覧画面をカスタマイズします。

## 完成版プロジェクト

<https://github.com/shun-rec/django-website-14>

## 事前準備

前回から引き続いて受講している方は事前準備は不要です。

### 新規サーバーを立ち上げる

[Paiza](https://paiza.cloud)で作業している方はdjangoにチェックを入れて新規サーバーを立ち上げて下さい。  
自分のマシンで作業している方はdjangoが使える作業用フォルダを作成して下さい。

### 前回管理サイトをカスタマイズしたプロジェクトをダウンロード

ターミナルを開いて、以下を実行。

```sh
git clone https://github.com/shun-rec/django-website-13
```

フォルダを移動

```sh
cd django-website-13
```

### マイグレートしてDBを作成

```sh
python manage.py migrate
```

### スーパーユーザーを作成

```sh
python manage.py createsuperuser
```

* ユーザー名: admin
* メールアドレス: （無し）
* パスワード: admin

### 動かしてみよう

```py
python manage.py runserver
```

`/staff-admin/`にアクセスして、前回作成した管理画面が表示されればOKです。

## フィールドを変更しよう

現在はモデルの編集画面で各項目がフィールド名そのまま英語で表示されています。  
これを自分で設定した日本語のものに変えましょう。

モデルの各フィールドに`verbose_name`引数で文字列を渡すことで設定する事ができます。

今回は`Post`モデルの各フィールドを日本語に変えてみましょう。

### created

まずは`Post`モデルの`created`フィールドの最後に以下のように`verbose_name="作成日"`と追加しましょう。

`blog/models.py`

```py
    created = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        blank=False,
        null=False,
        verbose_name="作成日"
    )
```

同じ要領ですべてのフィールドの最後に`verbose_name`を追加しましょう。

### updated

```py
        verbose_name="最終更新日"
```

### title

```py
        verbose_name="タイトル"
```

### body

```py
        verbose_name="本文",
```

### category

```py
        verbose_name="カテゴリ"
```

### tags

```py
        verbose_name="タグ"
```

### published

```py
        verbose_name="公開する"
```

### 動かしてみよう

Post編集ページで各項目が今設定したものに変わっていればOKです。

## フィールドにユーザーのヘルプ文言を表示しよう

項目の入力に説明がないと不親切なときはユーザーにヘルプ文言を表示しましょう。

モデルのフィールドに`help_text`で文字列を渡すことで設定できます。

今回は本文に「HTMLタグは使えません。」というヘルプ文言を表示してみましょう。

`blog/models.py`の`Post`モデルの`body`フィールドの最後に以下を追記します。

```py
        help_text="HTMLタグは使えません。"
```

## 表示するフィールドを制御しよう

編集ページで非表示にしたい項目があることがあります。  
その場合には`AdminModel`に`fields`を指定することで表示される項目を選択することが出来ます。  
デフォルトでは、編集可能な項目はすべて表示されます。

今回は一時的にタイトルだけが表示されるようにしてみましょう。

`blog/admin.py`の`PostAdmin`の先頭に以下を追記しましょう。  
タプルな要素１つの場合末尾に`,`をつける必要があることに注意して下さい。

```py
    fields = ('title',)
```

タイトルだけが表示できたことが確認出来たら、表示をもとに戻しましょう。

```py
    fields = ('title', 'body', 'category', 'tags')
```

## 編集不可な項目を表示しよう

編集な出来なくても項目の表示だけはしたいことがあります。  
`readonly_fields`にフィールド名を指定することで表示できます。  
注意点として、`fields`に指定されていないフィールドの場合は`fields`にも追加が必要です。

`blog/admin.py`の`PostAdmin`の先頭を以下のように書き換えましょう。

```py
    readonly_fields = ('created', 'updated')
    fields = ('title', 'body', 'category', 'tags', 'created', 'updated')
```

## フォームのフィールドを分類しよう

項目を分かりやすく分類して表示するには`fieldsets`を使います。  
指定の仕方が複雑なので以下のサンプルを参考にして下さい。  
分類をタプルのリストで表現します。  
タプルの1つ目の要素に分類のタイトルを2つ目の要素にその分類に入れる項目を指定します。  
タイトルは`None`にするとヘッダが非表示になります。
注意点として、`fieldsets`を使用する際には`fields`は削除します。

今回は以下のように分類してみます。  
`blog/admin.py`の`PostAdmin`の`fields`を削除して、`readonly_fields`の下に以下を追記します。

```py
    fieldsets = [
        (None, {'fields': ('title', )}),
        ('コンテンツ', {'fields': ('body', )}),
        ('分類', {'fields': ('category', 'tags')}),
        ('メタ', {'fields': ('created', 'updated')})
    ]
```

## フォームのさらなるカスタマイズ

さらなるカスタマイズが必要な場合、独自のフォームを指定することも出来ます。  
モデルで共通で使うことも出来ます。

今回は項目のタイトルをさらに変更するために独自フォームを使用してみます。

`blog/admin.py`の`PostAdmin`の上に以下を追記します。

```py
from django import forms

class PostAdminForm(forms.ModelForm):
    class Meta:
        labels = {
            'title': 'ブログタイトル',
        }
```

そして、`PostAdmin`の中に`form`を追記して先程作ったフォームを指定します。

```py
    form = PostAdminForm
```

フォームについて詳細は第７回、第８回を参照して下さい。

## バリデーションの追加

普通はモデルに追加するのが良いことが多いです。  
それが出来ない場合はFormに追加することも出来ます。

今回は本文にHTMLタグが使われていたらエラーが表示されるようにします。

`blog/admin.py`の`PostAdminForm`のメソッドとして以下を追記します。

```py
    def clean(self):
        body = self.cleaned_data.get('body')
        if '<' in body:
            raise forms.ValidationError('HTMLタグは使えません。')
```

## 多対多フィールドを選択しやすくしよう

`Post`のタグのようにManyToManyフィールドはデフォルトでは選択しにくいものになっています。  
これを左に未選択のもの、右に選択中のもの、と分かりやすくしてみます。  
`filter_horizontal`に対象のManyToManyフィールド名を指定します。

今回はタグをそのように変更してみます。  

`blog/admin.py`の`PostAdmin`の`form`の下に以下を追記します。

```py
    filter_horizontal = ('tags',)
```

## 関連モデルも同時に修正 - インライン

ForeignKeyフィールドやOneToOneフィールドを使っている場合に、関連するモデルも一緒に編集したいことがあります。  
１つのページに関連する２つ以上モデルを表示するには`inline`というものを使用します。

今回はカテゴリ編集ページにそのカテゴリのブログ一覧を表示してみます。

### インラインクラスの追加

`blog/admin.py`の`CategoryAdmin`の上に以下のクラスを追加します。

```py
class PostInline(admin.TabularInline):
    model = models.Post
    fields = ('title', 'body')
    extra = 1
```

* インラインを作るには`admin.TabularInline`というクラスを継承します
* modelに表示するモデルを指定します
* fieldsに編集させるフィールドを列挙します
* extraに新規追加用の空白フォームの数を指定します

### 自作のインラインクラスを指定

今作ったインラインクラスを指定するには、`inline`という配列に追加します。

`blog/admin.py`の`CategoryAdmin`の中に以下を追記します。

```py
    inlines = [PostInline]
```

## 保存時に処理を追加

データの保存前後に独自の処理を入れたいことがあります。  
例えばデフォルトのタグを追加したりなどです。

その場合には`save_model`メソッドを上書きします。

今回は保存の前後に`print`分でログの表示だけをしてみましょう。

`blog/admin.py`の`PostAdmin`に以下を追記します。  
`print`文のところに独自の処理を入れるとそれが実行されます。

```
    def save_model(self, request, obj, form, change):
        print("before save")
        super().save_model(request, obj, form, change)
        print("after save")
```

## 新規作成フォームと編集フォームのテンプレートの上書き

`change_form.html`というファイルを上書きすることで、編集ページのデザインを変更することが出来ます。  
どこにこのファイルを置くかでデザインの適用範囲が変わってきます。  

* admin直下: 全モデル。
* admin/<アプリ名>/: 特定のアプリのみ
* admin/<アプリ名>/<モデル名>/: 特定のモデルのみ

今回は、以下のような注意書きをページ先頭に追加してみます。

* ブログ編集ページ: 「すべてのフィールドが必須です。」
* その他のページ: 「カテゴリ、タグの追加・編集は管理者のみ行って下さい」

まずはその他のページから。

Postモデル以外すべてに適用したいので、`templates/admin/blog/`以下に配置します。

`templates/admin/blog/change_form.html`

```html
{% extends "admin/change_form.html" %}

{% block content %}
    <h2>カテゴリ、タグの追加・編集は管理者のみ行って下さい。</h2>
    {{ block.super }}
{% endblock %}
```

ブログ編集ページの変更はこのページだけに適用したいので、さらに`post/`フォルダの中に配置します。

`templates/admin/blog/post/change_form.html`

```html
{% extends "admin/change_form.html" %}

{% block content %}
    <h2>すべてのフィールドが必須です。</h2>
    {{ block.super }}
{% endblock %}
```

## JSの読み込み

ページを再読み込みせずにリアルタイムに処理を行いたいことがあります。  
それにはJavascriptが必要になります。  
独自のJavascriptを読み込んでみましょう。  
djangoの管理画面ではデフォルトでjQueryが使用できるようになっています。
独自のJavascriptの中でもjQueryが使用可能です。

今回は投稿編集ページでアラートダイアログを表示してみましょう。

`static/post.js`というファイルを新規作成し、以下の内容を追記します。

```js
(function($) {
  $(document).ready(function() {
    alert("JSが読み込まれました。")
  });
})(django.jQuery || jQuery);
```

`blog/admin.py`の`PostAdmin`の中に以下のインナークラスを追加します。

```py
    class Media:
        js = ('post.js',)
```

* jsに読み込みたいJavascriptファイルを列挙します。

ページを開いた時にアラートダイアログが表示されればOKです。
