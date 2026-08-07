# 一級建築士 学科 2027

51週の学習計画を GitHub 上で回すための最小構成です。
**計画と進捗だけ**を扱います。ノートと暗記カードは今のところ含みません。

---

## セットアップ

```bash
unzip kenchikushi-2027.zip && cd kenchikushi-2027
git init && git add -A && git commit -m "init"
gh repo create kenchikushi-2027 --private --source=. --push
```

`.github` は隠しフォルダです。**GitHub の Web にドラッグして上げると抜け落ちます。** コマンドラインか GitHub Desktop を使ってください。

そのあと GitHub 側で2か所だけ設定します。

1. **Settings → Pages** → Source を `main / docs` に（UI が公開されます）
2. **Settings → Actions → General → Workflow permissions** → **Read and write** に

`data/plan.yaml` の `repo:` に `owner/repo` を書いておくと、UI から週次 Issue へ飛べます。

---

## 何がどこにあるか

| | |
|---|---|
| `data/plan.yaml` | **唯一の原本。** 51週の構成・単元・章・重み |
| `data/log.yaml` | 記録。ここだけを更新すれば進捗が反映される |
| `docs/` | GitHub Pages。`state.js` `state.json` `plan.ics` は自動生成 |
| `scripts/` | build / ics / issue 生成・同期 |
| `.github/workflows/` | 月曜の Issue 生成、push 時の再計算 |

---

## 学習サイクル

毎週3〜4本のトラックが同時に走ります。**チェックの単位もこれです。**

| トラック | 内容 | 配分 |
|---|---|---|
| 新規 | 今週の単元 + 該当範囲の過去問 | 60% |
| 復習 | 先週の範囲を読み直す | 10% |
| 過去問 | 先々週範囲を時間計測で | 20% |
| 累積 | 既習範囲から20問 | 10% |

`計画 → 環境 → 法規 → 構造 → 施工` を 8 周します。

### 単元番号 = ローテーション番号

**同じ番号の単元は同じ5週間に学習されます。** そこを使って、科目をまたいで関連する章を同じ番号に置いてあります。章番号順ではありません。

| R | 主な連結 |
|---|---|
| 2 | 環境の採光・換気 ↔ 法規2章の 1/7・1/20 規定 ↔ 計画の各部寸法 |
| 3 | 環境の音響・色彩 ↔ 計画の劇場・ホール ↔ 施工の内装仕上げ |
| 4 | 環境の日影 ↔ 法規の日影規制 ↔ 計画の都市計画 ／ **構造の地盤・基礎 ↔ 施工の地盤調査・山留・杭** |
| 5 | 法規3章 構造強度（計算ルート）↔ 構造の一次設計・構造計画 |
| 6 | 構造のRC ↔ 施工のコンクリート・PCa |
| 7 | 構造のS造 ↔ 施工の鉄骨 ／ 環境の消火・防災設備 ↔ 法規5章 建築設備 |
| 8 | 計画の建築生産 ↔ 法規の建築士法・建設業法 ／ 環境の給排水・電気 ↔ 施工の設備工事 |

`plan.yaml` の `units:` を並べ替えるとここが崩れます。動かすときは `links:` も直してください。

---

## 記録のしかた

**経路は2本です。どちらか片方に寄せた方が混乱しません。**

### A. 週次 Issue（スマホ向き）

毎週月曜0時（JST）に Actions が Issue を立てます。トラックにチェックを入れると `log.yaml` に自動で反映されます。

### B. `data/log.yaml` を直接編集（PC向き）

```yaml
W04:
  new: true
  review: true
  exam: false
  cum: false
  hours: 15
```

UI の「記録をコピー」を押すと、この形がそのままクリップボードに入ります。

遅れたら `status: slipped` と `moved_to: 16` を手で書きます。チャートに点線のゴーストが残ります。

---

## 端末間の同期

### 方法1  週次 Issue（設定不要）

GitHub アプリにログインしていれば、それがそのまま同期です。Issue のトラックにチェックを入れると Actions が `log.yaml` を書き換えます。**追加の設定はありません。**

### 方法2  UI から直接（推奨・要トークン）

ページ下部の「書き出しと設定 → 端末間の同期」に入力すると、チェックがそのまま `data/log.yaml` に保存されます。

1. GitHub → Settings → Developer settings → **Fine-grained personal access tokens** → Generate new token
2. **Repository access** = Only select repositories → このリポジトリだけ
3. **Permissions → Repository permissions → Contents** = **Read and write**（他は触らない）
4. Expiration は 90日など短めに
5. 発行された `github_pat_...` を UI に貼り、`owner/repo` と一緒に「接続」

以後、チェックすると約1秒後に自動保存されます。別の端末でページを開くと最新が読み込まれ、タブに戻るたびにも取り直します。

**セキュリティ上の注意**
トークンはブラウザの localStorage に保存されます。GitHub Pages は `username.github.io` という**同一オリジンを全プロジェクトで共有する**ので、同じアカウントの他の Pages サイトから読める可能性があります。だから権限を Contents だけ・対象を1リポジトリだけに絞り、期限を短くしてください。最悪の場合でも被害はこのリポジトリの中身に限定されます。

気になる場合は方法1（Issue）だけを使ってください。**機能は同じです。**

### 反映のしくみ

```
スマホで Issue にチェック
  ↓ 数十秒   Actions が log.yaml を更新 → state を再計算 → commit
  ↓ 30秒ほど GitHub Pages が配信
PC でページを開くと反映されている
```

ページは開くたびに `state.json` をキャッシュ無効で取り直します。フッターに `state 2026-11-02 ／ 表示 11/02 21:34` と出るので、いつのデータかを確認できます。

**反映まで1〜2分**かかります。即時ではありません。

未接続のときは、UI のチェックはページ内だけの状態です。「記録をコピー」で `log.yaml` に貼るか、Issue を使ってください。

---

## 手で動かす

```bash
pip install pyyaml
python3 scripts/build.py            # state を作り直す
python3 scripts/gen_ics.py          # docs/plan.ics
python3 scripts/gen_issue.py 19     # W19 の Issue 本文を表示
```

Actions からも `weekly` を手動実行できます（週番号を指定可）。

---

## 注意

- 本試験日 `2027-07-25` は見込みです。**2027年1月の公告で必ず確認**して `plan.yaml` を直してください
- 法令集は W22（2026年12月末）に2027年版を買って線引きします
- `docs/state.js` `docs/state.json` `docs/plan.ics` は自動生成です。手で直しても次のビルドで消えます
