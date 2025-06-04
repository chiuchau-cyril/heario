# **🧭 News Card Picker Prototype — Next.js + Firebase 技術文件**

## **🎯 目標功能**

* 顯示來自 **newsapi.org** 的新聞卡片
* 使用者可以勾選新聞組成「新聞集」
* 使用者登入（Google OAuth）
* 將新聞集儲存至 Firebase Firestore
* 顯示個人歷史新聞集

---

## **📦 技術棧**

| **類別** | **技術**                    |
| -------------- | --------------------------------- |
| 前端框架       | Next.js 14+ (App Router)          |
| UI             | Tailwind CSS（可替代）            |
| 第三方新聞 API | [newsapi.org](https://newsapi.org/)  |
| 身份驗證       | Firebase Authentication（Google） |
| 後端資料儲存   | Firebase Firestore                |
| 環境變數管理   | .env.local                        |

---

## **📁 專案結構建議**

```
/app
  /news
    page.tsx            // 顯示新聞卡片頁
    NewsCard.tsx        // 卡片元件
    useNews.ts          // 抓取新聞 API 的 hook
  /dashboard
    page.tsx            // 顯示已儲存新聞集
/firebase
  client.ts             // 初始化 client SDK
  firestore.ts          // Firestore 操作封裝
  auth.ts               // 登入、登出邏輯
/lib
  utils.ts              // 格式轉換、清理 API 回傳資料
```

---

## **🔐 Firebase Auth 設定（Google 登入）**

```
// /firebase/auth.ts
import { getAuth, GoogleAuthProvider, signInWithPopup, signOut } from "firebase/auth";
import { app } from './client';

const auth = getAuth(app);

export const login = async () => {
  const provider = new GoogleAuthProvider();
  return await signInWithPopup(auth, provider);
};

export const logout = async () => {
  return await signOut(auth);
};

export const onAuthStateChanged = (callback: (user: any) => void) => {
  return auth.onAuthStateChanged(callback);
};
```

---

## **☁️ Firestore 結構**

### **🔐** ****

### **users**

### ** 集合**

```
{
  "uid": "firebase_uid",
  "email": "user@example.com",
  "displayName": "使用者名稱",
  "createdAt": "2025-06-04T00:00:00Z"
}
```

### **📰** ****

### **news_sets**

### ** 集合**

```
{
  "uid": "firebase_uid",
  "title": "2025/6/4 精選新聞",
  "createdAt": "...",
  "articles": [
    {
      "title": "...",
      "description": "...",
      "url": "...",
      "urlToImage": "...",
      "source": "CNN",
      "publishedAt": "..."
    }
  ]
}
```

---

## **🌐 抓取 NewsAPI（Client-side）**

```
// /app/news/useNews.ts
export async function fetchTopNews() {
  const res = await fetch(
    `https://newsapi.org/v2/top-headlines?country=tw&pageSize=20&apiKey=${process.env.NEWS_API_KEY}`
  );
  const data = await res.json();
  return data.articles;
}
```

> 🔐 將 API Key 放在 **.env.local**：

```
NEWS_API_KEY=your_news_api_key
NEXT_PUBLIC_FIREBASE_API_KEY=...
```

---

## **🖼 UI：新聞卡片（簡略版）**

```
// /app/news/NewsCard.tsx
export function NewsCard({ article, onSelect, selected }) {
  return (
    <div className="border p-4">
      <img src={article.urlToImage} alt="" />
      <h2>{article.title}</h2>
      <p>{article.description}</p>
      <label>
        <input
          type="checkbox"
          checked={selected}
          onChange={() => onSelect(article)}
        />
        選取
      </label>
    </div>
  );
}
```

---

## **📝 儲存選取新聞至 Firestore**

```
// /firebase/firestore.ts
import { getFirestore, collection, addDoc } from "firebase/firestore";
import { app } from './client';

const db = getFirestore(app);

export const saveNewsSet = async (uid: string, title: string, articles: any[]) => {
  await addDoc(collection(db, "news_sets"), {
    uid,
    title,
    articles,
    createdAt: new Date().toISOString()
  });
};
```

---

## **✅ 任務分解**

| **任務**  | **負責模組**      |
| --------------- | ----------------------- |
| Google 登入     | /firebase/auth.ts       |
| 抓新聞資料      | /app/news/useNews.ts    |
| 顯示卡片 + 勾選 | /app/news/NewsCard.tsx  |
| 儲存新聞集      | /firebase/firestore.ts  |
| 顯示歷史紀錄    | /app/dashboard/page.tsx |
