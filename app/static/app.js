(function () {
  const KNOWN_ROUTES = new Set(["/", "/tried", "/ratings/new", "/settings"]);
  const STORAGE_KEYS = {
    token: "gwf_token",
    locale: "gwf_locale",
    activeUser: "gwf_active_user",
  };

  const I18N = {
    en: {
      appTitle: "Guadalajara Wine Finder",
      subtitle: "Batch-first recommendations for User A and User B.",
      home: "Home",
      tried: "Tried Wines",
      addRating: "Add Rating",
      settings: "Settings",
      activeUser: "Active User",
      language: "Language",
      login: "Login",
      logout: "Logout",
      password: "Password",
      loggedInAs: "Logged in as",
      notLoggedIn: "Not logged in",
      freshness: "Data Freshness",
      fresh: "Fresh",
      stale: "Stale",
      noData: "No data yet",
      refreshHealth: "Refresh Health",
      manualRun: "Trigger Manual Run",
      scheduleMode: "Schedule Mode",
      runStatus: "Run Status",
      recommendedBuys: "Recommended Buys",
      cheapestFavorites: "Cheapest Favorites",
      noRecommendations: "No recommendations available yet.",
      why: "Why this recommendation",
      unknown: "Unknown",
      searchName: "Search name",
      wineType: "Wine type",
      grape: "Grape",
      search: "Search",
      clear: "Clear",
      lastKnownPrice: "Last known price",
      history: "Rating History",
      noTriedWines: "No tried wines found.",
      wineId: "Wine ID",
      rating: "Rating",
      comment: "Comment",
      triedAt: "Tried at",
      submitRating: "Submit Rating",
      ratingSuccess: "Rating saved successfully.",
      ratingDeleted: "Rating deleted.",
      triggerHint: "If recommendations are empty, trigger a manual run.",
      authRequired: "Please login to load user-specific data.",
      runCompleted: "Run completed successfully.",
      routeNotFound: "Route not found. Redirected to Home.",
      invalidRating: "Rating must be from 1 to 5.",
      invalidWineId: "Wine ID must be a positive number.",
      modeDaily: "daily",
      modeWeekly: "weekly",
      modeManual: "manual",
      tableWine: "Wine",
      tableLastRating: "Last rating",
      tableRatingsCount: "Ratings count",
      tablePrice: "Price",
      tableAction: "Action",
      view: "View",
      recommendationRank: "Rank",
      recommendationScore: "Score",
      recommendationPrice: "Price",
      recommendationOffer: "Offer",
      recommendationWine: "Wine",
      recommendationStore: "Store",
      unauthorizedRun: "Manual run is only available for User A.",
      loginFailed: "Login failed. Check credentials.",
      recommendationError: "Unable to load recommendations.",
      triedError: "Unable to load tried wines.",
      settingsHelp: "Use these controls to manage locale, active user, and pipeline runs.",
      saveSettings: "Save User Settings",
      settingsSaved: "User settings saved.",
      loginHelp: "Login is required for recommendations, tried wines, and ratings.",
      userALabel: "A — Alexander",
      userBLabel: "B — Elena",
      delete: "Delete",
      deleteConfirm: "Delete this rating?",
      userSettings: "User Configuration",
      pageStatus: "Status",
      loading: "Loading...",
      notAvailable: "N/A",
    },
    ru: {
      appTitle: "Guadalajara Wine Finder",
      subtitle: "Пакетные рекомендации для пользователей A и B.",
      home: "Главная",
      tried: "Пробованные вина",
      addRating: "Добавить оценку",
      settings: "Настройки",
      activeUser: "Активный пользователь",
      language: "Язык",
      login: "Войти",
      logout: "Выйти",
      password: "Пароль",
      loggedInAs: "Выполнен вход как",
      notLoggedIn: "Вход не выполнен",
      freshness: "Свежесть данных",
      fresh: "Свежие",
      stale: "Устарели",
      noData: "Пока нет данных",
      refreshHealth: "Обновить статус",
      manualRun: "Запустить вручную",
      scheduleMode: "Режим расписания",
      runStatus: "Статус запуска",
      recommendedBuys: "Рекомендованные покупки",
      cheapestFavorites: "Самые дешевые фавориты",
      noRecommendations: "Рекомендации пока недоступны.",
      why: "Причины рекомендации",
      unknown: "Неизвестно",
      searchName: "Поиск по названию",
      wineType: "Тип вина",
      grape: "Сорт винограда",
      search: "Поиск",
      clear: "Очистить",
      lastKnownPrice: "Последняя известная цена",
      history: "История оценок",
      noTriedWines: "Пробованные вина не найдены.",
      wineId: "ID вина",
      rating: "Оценка",
      comment: "Комментарий",
      triedAt: "Дата дегустации",
      submitRating: "Сохранить оценку",
      ratingSuccess: "Оценка успешно сохранена.",
      ratingDeleted: "Оценка удалена.",
      triggerHint: "Если рекомендации пустые, запустите ручной прогон.",
      authRequired: "Войдите, чтобы загрузить пользовательские данные.",
      runCompleted: "Прогон успешно завершен.",
      routeNotFound: "Маршрут не найден. Выполнен переход на главную.",
      invalidRating: "Оценка должна быть от 1 до 5.",
      invalidWineId: "ID вина должен быть положительным числом.",
      modeDaily: "ежедневно",
      modeWeekly: "еженедельно",
      modeManual: "вручную",
      tableWine: "Вино",
      tableLastRating: "Последняя оценка",
      tableRatingsCount: "Количество оценок",
      tablePrice: "Цена",
      tableAction: "Действие",
      view: "Открыть",
      recommendationRank: "Ранг",
      recommendationScore: "Оценка",
      recommendationPrice: "Цена",
      recommendationOffer: "Предложение",
      recommendationWine: "Вино",
      recommendationStore: "Магазин",
      unauthorizedRun: "Ручной запуск доступен только пользователю A.",
      loginFailed: "Ошибка входа. Проверьте учетные данные.",
      recommendationError: "Не удалось загрузить рекомендации.",
      triedError: "Не удалось загрузить пробованные вина.",
      settingsHelp: "Здесь можно изменить язык, пользователя и запустить pipeline.",
      saveSettings: "Сохранить настройки пользователя",
      settingsSaved: "Настройки пользователя сохранены.",
      loginHelp: "Для рекомендаций, оценок и истории нужен вход.",
      userALabel: "A — Александр",
      userBLabel: "B — Елена",
      delete: "Удалить",
      deleteConfirm: "Удалить эту оценку?",
      userSettings: "Конфигурация пользователя",
      pageStatus: "Статус",
      loading: "Загрузка...",
      notAvailable: "Н/Д",
    },
  };

  const state = {
    route: normalizeRoute(window.location.pathname),
    locale: sessionStorage.getItem(STORAGE_KEYS.locale) || "en",
    activeUser: sessionStorage.getItem(STORAGE_KEYS.activeUser) || "A",
    token: sessionStorage.getItem(STORAGE_KEYS.token) || "",
    loginPassword: "",
    me: null,
    health: null,
    runInfo: null,
    status: { type: "no_data", text: "" },
    loading: {
      health: false,
      recommended: false,
      favorites: false,
      tried: false,
      ratingSubmit: false,
      runTrigger: false,
      runInfo: false,
      settingsSave: false,
    },
    recommended: [],
    favorites: [],
    tried: [],
    selectedWineId: null,
    triedFilters: { query: "", wine_type: "", grape: "" },
    ratingForm: { wine_id: "", rating_1_5: "4", comment: "", tried_at: "" },
    runMode: "manual",
  };

  state.loginPassword = defaultPassword(state.activeUser);

  function normalizeRoute(pathname) {
    if (KNOWN_ROUTES.has(pathname)) return pathname;
    return "/";
  }

  function t(key) {
    return I18N[state.locale][key] || I18N.en[key] || key;
  }

  function defaultPassword(userId) {
    return userId === "A" ? "changeme-a" : "changeme-b";
  }

  function unknown(value) {
    if (value === null || value === undefined || value === "") return t("unknown");
    return String(value);
  }

  function formatDate(value) {
    if (!value) return t("unknown");
    try {
      return new Date(value).toLocaleString(state.locale === "ru" ? "ru-RU" : "en-US");
    } catch (error) {
      return String(value);
    }
  }

  function escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function setStatus(type, text) {
    state.status = { type, text };
    render();
  }

  function saveSession() {
    sessionStorage.setItem(STORAGE_KEYS.locale, state.locale);
    sessionStorage.setItem(STORAGE_KEYS.activeUser, state.activeUser);
    if (state.token) sessionStorage.setItem(STORAGE_KEYS.token, state.token);
    else sessionStorage.removeItem(STORAGE_KEYS.token);
  }

  async function api(path, options = {}) {
    const headers = { Accept: "application/json", ...(options.headers || {}) };
    if (state.token) headers.Authorization = `Bearer ${state.token}`;
    if (options.body && !headers["Content-Type"]) headers["Content-Type"] = "application/json";

    const response = await fetch(path, { ...options, headers });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      if (response.status === 401) {
        state.token = "";
        state.me = null;
        saveSession();
      }
      throw new Error(payload.detail || `HTTP ${response.status}`);
    }
    return payload;
  }

  function navigate(path) {
    const target = normalizeRoute(path);
    if (target !== path) {
      setStatus("status-error", t("routeNotFound"));
    }
    if (window.location.pathname !== target) window.history.pushState({}, "", target);
    state.route = target;
    state.selectedWineId = null;
    render();
    void loadRouteData();
  }

  function statusBadgeClass() {
    if (!state.health) return "status-no_data";
    return state.health.data_freshness === "fresh" ? "status-fresh" : "status-stale";
  }

  function statusBadgeText() {
    if (!state.health) return t("noData");
    if (state.health.data_freshness === "fresh") return t("fresh");
    if (state.health.data_freshness === "stale") return t("stale");
    return t("noData");
  }

  function navLink(path, label) {
    const current = state.route === path;
    return `<a href="${path}" class="nav-tab" data-action="route" data-route="${path}" ${
      current ? 'aria-current="page"' : ""
    }>${escapeHtml(label)}</a>`;
  }

  function skeletonRecommendationList(count) {
    return Array.from({ length: count })
      .map(
        () => `
          <article class="skeleton-card" aria-hidden="true">
            <div class="skeleton skeleton-line" style="width: 45%;"></div>
            <div class="skeleton skeleton-line" style="width: 80%;"></div>
            <div class="skeleton skeleton-line" style="width: 60%;"></div>
            <div class="skeleton skeleton-line" style="width: 90%;"></div>
          </article>
        `
      )
      .join("");
  }

  function recommendationCards(items) {
    if (!items.length) return `<p class="muted">${escapeHtml(t("noRecommendations"))}</p>`;
    return items
      .map((item) => {
        const bullets = String(item.explanation || "")
          .split("\n")
          .map((line) => line.replace(/^•\s*/, "").trim())
          .filter(Boolean)
          .slice(0, 4)
          .map((line) => `<li>${escapeHtml(line)}</li>`)
          .join("");

        return `
          <article class="recommendation-card">
            <div class="recommendation-meta">
              <span><strong>${escapeHtml(t("recommendationRank"))}:</strong> ${escapeHtml(item.rank)}</span>
              <span><strong>${escapeHtml(t("recommendationWine"))}:</strong> #${escapeHtml(item.wine_id)}</span>
              <span><strong>${escapeHtml(t("recommendationOffer"))}:</strong> ${escapeHtml(item.offer_id || t("unknown"))}</span>
              <span><strong>${escapeHtml(t("recommendationScore"))}:</strong> ${escapeHtml(item.score.toFixed(3))}</span>
              <span><strong>${escapeHtml(t("recommendationPrice"))}:</strong> ${escapeHtml(t("unknown"))}</span>
            </div>
            <p class="muted">${escapeHtml(t("recommendationStore"))}: ${escapeHtml(t("unknown"))}</p>
            <p><strong>${escapeHtml(t("why"))}</strong></p>
            <ul>${bullets || `<li>${escapeHtml(t("notAvailable"))}</li>`}</ul>
          </article>
        `;
      })
      .join("");
  }

  function selectedWineDetail() {
    if (!state.selectedWineId) return `<p class="muted">${escapeHtml(t("history"))}: ${escapeHtml(t("notAvailable"))}</p>`;
    const wine = state.tried.find((row) => row.wine_id === state.selectedWineId);
    if (!wine) return `<p class="muted">${escapeHtml(t("unknown"))}</p>`;
    const ratings = (wine.ratings || [])
      .map(
        (entry) => `
          <li>
            <strong>${escapeHtml(entry.rating_1_5)}/5</strong>
            — ${escapeHtml(formatDate(entry.tried_at))}
            <br />
            <span>${escapeHtml(entry.comment || t("unknown"))}</span>
            ${
              entry.rating_id
                ? `<br /><button class="button button-secondary" data-action="delete-rating" data-rating-id="${escapeHtml(
                    entry.rating_id
                  )}">${escapeHtml(t("delete"))}</button>`
                : ""
            }
          </li>
        `
      )
      .join("");
    return `
      <div class="wine-detail">
        <h3>${escapeHtml(wine.canonical_name)}</h3>
        <p class="muted">${escapeHtml(t("lastKnownPrice"))}: ${
          wine.last_known_offer_price !== null ? escapeHtml(`${wine.last_known_offer_price} MXN`) : escapeHtml(t("unknown"))
        }</p>
        <p><strong>${escapeHtml(t("history"))}</strong></p>
        <ul>${ratings || `<li>${escapeHtml(t("unknown"))}</li>`}</ul>
      </div>
    `;
  }

  function renderHomePage() {
    return `
      <section class="panel">
        <h2>${escapeHtml(t("home"))}</h2>
        <p class="muted">${escapeHtml(t("triggerHint"))}</p>
        <div class="inline">
          <button class="button button-secondary" data-action="refresh-health">${escapeHtml(t("refreshHealth"))}</button>
          <button
            class="button"
            data-action="trigger-run"
            ${state.loading.runTrigger ? "disabled" : ""}
            ${state.me && state.me.id === "A" ? "" : "disabled"}
          >${state.loading.runTrigger ? escapeHtml(t("loading")) : escapeHtml(t("manualRun"))}</button>
        </div>
        <p class="muted">${escapeHtml(t("runStatus"))}: ${
          state.runInfo ? `${escapeHtml(state.runInfo.status)} (${escapeHtml(state.runInfo.run_id || t("unknown"))})` : escapeHtml(t("unknown"))
        }</p>
      </section>
      <section class="panel">
        <h2>${escapeHtml(t("recommendedBuys"))}</h2>
        <div class="recommendation-list" aria-busy="${state.loading.recommended ? "true" : "false"}">
          ${
            state.loading.recommended
              ? skeletonRecommendationList(3)
              : recommendationCards(state.recommended)
          }
        </div>
      </section>
      <section class="panel">
        <h2>${escapeHtml(t("cheapestFavorites"))}</h2>
        <div class="recommendation-list" aria-busy="${state.loading.favorites ? "true" : "false"}">
          ${
            state.loading.favorites
              ? skeletonRecommendationList(2)
              : recommendationCards(state.favorites)
          }
        </div>
      </section>
    `;
  }

  function renderTriedPage() {
    const rows = state.tried
      .map((wine) => {
        const latest = wine.ratings?.[0];
        return `
          <tr>
            <td>${escapeHtml(wine.canonical_name)}</td>
            <td>${latest ? escapeHtml(`${latest.rating_1_5}/5`) : escapeHtml(t("unknown"))}</td>
            <td>${escapeHtml((wine.ratings || []).length)}</td>
            <td>${wine.last_known_offer_price !== null ? escapeHtml(`${wine.last_known_offer_price} MXN`) : escapeHtml(t("unknown"))}</td>
            <td>
              <button class="button button-secondary" data-action="select-wine" data-wine-id="${escapeHtml(
                wine.wine_id
              )}">${escapeHtml(t("view"))}</button>
            </td>
          </tr>
        `;
      })
      .join("");

    return `
      <section class="panel">
        <h2>${escapeHtml(t("tried"))}</h2>
        <div class="split">
          <div class="stack">
            <label>${escapeHtml(t("searchName"))}
              <input id="queryInput" value="${escapeHtml(state.triedFilters.query)}" />
            </label>
            <label>${escapeHtml(t("wineType"))}
              <select id="wineTypeInput">
                <option value="">${escapeHtml(t("unknown"))}</option>
                <option value="red" ${state.triedFilters.wine_type === "red" ? "selected" : ""}>red</option>
                <option value="white" ${state.triedFilters.wine_type === "white" ? "selected" : ""}>white</option>
                <option value="rose" ${state.triedFilters.wine_type === "rose" ? "selected" : ""}>rose</option>
                <option value="sparkling" ${state.triedFilters.wine_type === "sparkling" ? "selected" : ""}>sparkling</option>
                <option value="other" ${state.triedFilters.wine_type === "other" ? "selected" : ""}>other</option>
              </select>
            </label>
            <label>${escapeHtml(t("grape"))}
              <input id="grapeInput" value="${escapeHtml(state.triedFilters.grape)}" />
            </label>
            <div class="inline">
              <button class="button" data-action="search-tried">${escapeHtml(t("search"))}</button>
              <button class="button button-secondary" data-action="clear-tried">${escapeHtml(t("clear"))}</button>
            </div>
          </div>
          <div>
            ${selectedWineDetail()}
          </div>
        </div>
      </section>
      <section class="panel">
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>${escapeHtml(t("tableWine"))}</th>
                <th>${escapeHtml(t("tableLastRating"))}</th>
                <th>${escapeHtml(t("tableRatingsCount"))}</th>
                <th>${escapeHtml(t("tablePrice"))}</th>
                <th>${escapeHtml(t("tableAction"))}</th>
              </tr>
            </thead>
            <tbody>
              ${
                state.loading.tried
                  ? `<tr><td colspan="5" class="muted">${escapeHtml(t("loading"))}</td></tr>`
                  : rows || `<tr><td colspan="5" class="muted">${escapeHtml(t("noTriedWines"))}</td></tr>`
              }
            </tbody>
          </table>
        </div>
      </section>
    `;
  }

  function renderRatingPage() {
    return `
      <section class="panel">
        <h2>${escapeHtml(t("addRating"))}</h2>
        <form id="ratingForm" class="form-grid">
          <label>${escapeHtml(t("wineId"))}
            <input id="wineIdInput" type="number" min="1" value="${escapeHtml(state.ratingForm.wine_id)}" required />
          </label>
          <label>${escapeHtml(t("rating"))}
            <select id="ratingInput">
              ${[1, 2, 3, 4, 5]
                .map(
                  (value) =>
                    `<option value="${value}" ${String(value) === String(state.ratingForm.rating_1_5) ? "selected" : ""}>${value}</option>`
                )
                .join("")}
            </select>
          </label>
          <label>${escapeHtml(t("triedAt"))}
            <input id="triedAtInput" type="datetime-local" value="${escapeHtml(state.ratingForm.tried_at)}" />
          </label>
          <label>${escapeHtml(t("comment"))}
            <textarea id="commentInput">${escapeHtml(state.ratingForm.comment)}</textarea>
          </label>
          <div class="inline">
            <button class="button" type="submit" ${state.loading.ratingSubmit ? "disabled" : ""}>${
              state.loading.ratingSubmit ? escapeHtml(t("loading")) : escapeHtml(t("submitRating"))
            }</button>
          </div>
        </form>
      </section>
    `;
  }

  function renderSettingsPage() {
    const run = state.runInfo;
    return `
      <section class="panel">
        <h2>${escapeHtml(t("settings"))}</h2>
        <p class="muted">${escapeHtml(t("settingsHelp"))}</p>
        <div class="form-grid">
          <p><strong>${escapeHtml(t("userSettings"))}</strong></p>
          <div class="inline">
            <button
              class="button button-secondary"
              data-action="save-user-settings"
              ${state.loading.settingsSave ? "disabled" : ""}
              ${state.token ? "" : "disabled"}
            >${state.loading.settingsSave ? escapeHtml(t("loading")) : escapeHtml(t("saveSettings"))}</button>
          </div>
          <label>${escapeHtml(t("scheduleMode"))}
            <select id="runModeInput">
              <option value="daily" ${state.runMode === "daily" ? "selected" : ""}>${escapeHtml(t("modeDaily"))}</option>
              <option value="weekly" ${state.runMode === "weekly" ? "selected" : ""}>${escapeHtml(t("modeWeekly"))}</option>
              <option value="manual" ${state.runMode === "manual" ? "selected" : ""}>${escapeHtml(t("modeManual"))}</option>
            </select>
          </label>
          <div class="inline">
            <button class="button button-secondary" data-action="reload-settings">${escapeHtml(t("refreshHealth"))}</button>
            <button
              class="button"
              data-action="trigger-run"
              ${state.me && state.me.id === "A" ? "" : "disabled"}
              ${state.loading.runTrigger ? "disabled" : ""}
            >${state.loading.runTrigger ? escapeHtml(t("loading")) : escapeHtml(t("manualRun"))}</button>
          </div>
          <p><strong>${escapeHtml(t("runStatus"))}:</strong> ${
            run
              ? `${escapeHtml(run.status || t("unknown"))} · ${escapeHtml(formatDate(run.finished_at || run.started_at))}`
              : escapeHtml(t("unknown"))
          }</p>
          ${
            run
              ? `<p class="muted">run_id=${escapeHtml(run.run_id || t("unknown"))} · stale_offer_count=${escapeHtml(
                  run.stale_offer_count ?? t("unknown")
                )}</p>`
              : ""
          }
        </div>
      </section>
    `;
  }

  function renderContent() {
    if (state.route === "/") return renderHomePage();
    if (state.route === "/tried") return renderTriedPage();
    if (state.route === "/ratings/new") return renderRatingPage();
    return renderSettingsPage();
  }

  function render() {
    document.documentElement.lang = state.locale;
    const app = document.getElementById("app");
    app.innerHTML = `
      <div class="container">
        <header class="shell-header">
          <h1 class="title">${escapeHtml(t("appTitle"))}</h1>
          <p class="subtitle">${escapeHtml(t("subtitle"))}</p>
          <div class="toolbar">
            <div class="toolbar-group">
              <label for="activeUserSelect">${escapeHtml(t("activeUser"))}</label>
              <select id="activeUserSelect">
                <option value="A" ${state.activeUser === "A" ? "selected" : ""}>${escapeHtml(t("userALabel"))}</option>
                <option value="B" ${state.activeUser === "B" ? "selected" : ""}>${escapeHtml(t("userBLabel"))}</option>
              </select>
            </div>
            <div class="toolbar-group">
              <label for="localeSelect">${escapeHtml(t("language"))}</label>
              <select id="localeSelect">
                <option value="en" ${state.locale === "en" ? "selected" : ""}>EN</option>
                <option value="ru" ${state.locale === "ru" ? "selected" : ""}>RU</option>
              </select>
            </div>
            <div class="toolbar-group">
              <label for="passwordInput">${escapeHtml(t("password"))}</label>
              <input
                id="passwordInput"
                type="password"
                autocomplete="current-password"
                value="${escapeHtml(state.loginPassword)}"
              />
              ${
                state.token && state.me
                  ? `<button class="button button-secondary" data-action="logout">${escapeHtml(t("logout"))}</button>`
                  : `<button class="button" data-action="login">${escapeHtml(t("login"))}</button>`
              }
            </div>
            <div class="toolbar-group">
              <span class="muted">${
                state.me
                  ? `${escapeHtml(t("loggedInAs"))}: ${escapeHtml(state.me.display_name)} (${escapeHtml(state.me.id)})`
                  : escapeHtml(t("notLoggedIn"))
              }</span>
            </div>
            <div class="toolbar-group">
              <span class="status-badge ${statusBadgeClass()}">
                ${escapeHtml(t("freshness"))}: ${escapeHtml(statusBadgeText())}
              </span>
            </div>
          </div>
          <p class="muted">${escapeHtml(t("loginHelp"))}</p>
          <nav class="nav-tabs" aria-label="Main Navigation">
            ${navLink("/", t("home"))}
            ${navLink("/tried", t("tried"))}
            ${navLink("/ratings/new", t("addRating"))}
            ${navLink("/settings", t("settings"))}
          </nav>
        </header>

        <main class="main-grid">${renderContent()}</main>
        <p class="aria-live ${escapeHtml(state.status.type || "status-no_data")}" aria-live="polite" role="status">
          ${escapeHtml(state.status.text)}
        </p>
      </div>
    `;
  }

  async function loadMe() {
    if (!state.token) {
      state.me = null;
      return;
    }
    try {
      state.me = await api("/users/me");
    } catch (error) {
      state.me = null;
      state.token = "";
      saveSession();
      setStatus("status-error", String(error.message || error));
    }
  }

  async function loadUserSettings() {
    if (!state.token) return;
    try {
      const settingsPayload = await api("/users/me/settings");
      if (settingsPayload && (settingsPayload.locale === "en" || settingsPayload.locale === "ru")) {
        state.locale = settingsPayload.locale;
        saveSession();
      }
    } catch (error) {
      setStatus("status-error", String(error.message || error));
    }
  }

  async function loadHealth() {
    state.loading.health = true;
    render();
    try {
      state.health = await api("/health");
    } catch (error) {
      setStatus("status-error", String(error.message || error));
    } finally {
      state.loading.health = false;
      render();
    }
  }

  async function loadRecommendations(kind) {
    if (!state.token) {
      setStatus("status-no_data", t("authRequired"));
      return;
    }
    if (kind === "recommended_buys") state.loading.recommended = true;
    if (kind === "cheapest_favorites") state.loading.favorites = true;
    render();

    try {
      const data =
        kind === "recommended_buys"
          ? await api("/recommendations?kind=recommended_buys")
          : await api("/favorites/cheapest");
      if (kind === "recommended_buys") state.recommended = data.items || [];
      if (kind === "cheapest_favorites") state.favorites = data.items || [];
    } catch (error) {
      setStatus("status-error", `${t("recommendationError")} ${String(error.message || error)}`);
      if (kind === "recommended_buys") state.recommended = [];
      if (kind === "cheapest_favorites") state.favorites = [];
    } finally {
      if (kind === "recommended_buys") state.loading.recommended = false;
      if (kind === "cheapest_favorites") state.loading.favorites = false;
      render();
    }
  }

  async function loadTriedWines() {
    if (!state.token) {
      setStatus("status-no_data", t("authRequired"));
      state.tried = [];
      render();
      return;
    }
    state.loading.tried = true;
    render();
    try {
      const params = new URLSearchParams();
      if (state.triedFilters.query) params.set("query", state.triedFilters.query);
      if (state.triedFilters.wine_type) params.set("wine_type", state.triedFilters.wine_type);
      if (state.triedFilters.grape) params.set("grape", state.triedFilters.grape);
      state.tried = await api(`/wines/tried?${params.toString()}`);
    } catch (error) {
      state.tried = [];
      setStatus("status-error", `${t("triedError")} ${String(error.message || error)}`);
    } finally {
      state.loading.tried = false;
      render();
    }
  }

  async function loadRunInfo() {
    state.loading.runInfo = true;
    render();
    try {
      state.runInfo = await api("/status/last-run");
    } catch (error) {
      state.runInfo = null;
      setStatus("status-error", String(error.message || error));
    } finally {
      state.loading.runInfo = false;
      render();
    }
  }

  async function triggerRun() {
    if (!state.me || state.me.id !== "A") {
      setStatus("status-error", t("unauthorizedRun"));
      return;
    }
    state.loading.runTrigger = true;
    render();
    try {
      state.runInfo = await api("/runs/trigger", {
        method: "POST",
        body: JSON.stringify({ mode: state.runMode }),
      });
      await loadHealth();
      await loadRouteData();
      setStatus("status-fresh", t("runCompleted"));
    } catch (error) {
      setStatus("status-error", String(error.message || error));
    } finally {
      state.loading.runTrigger = false;
      render();
    }
  }

  async function saveUserSettings() {
    if (!state.token) {
      setStatus("status-error", t("authRequired"));
      return;
    }
    state.loading.settingsSave = true;
    render();
    try {
      const payload = { locale: state.locale };
      await api("/users/me/settings", {
        method: "PATCH",
        body: JSON.stringify(payload),
      });
      setStatus("status-fresh", t("settingsSaved"));
    } catch (error) {
      setStatus("status-error", String(error.message || error));
    } finally {
      state.loading.settingsSave = false;
      render();
    }
  }

  async function submitRating() {
    if (!state.token) {
      setStatus("status-error", t("authRequired"));
      return;
    }
    const wineId = Number(state.ratingForm.wine_id);
    const rating = Number(state.ratingForm.rating_1_5);
    if (!Number.isFinite(wineId) || wineId < 1) {
      setStatus("status-error", t("invalidWineId"));
      return;
    }
    if (!Number.isFinite(rating) || rating < 1 || rating > 5) {
      setStatus("status-error", t("invalidRating"));
      return;
    }
    state.loading.ratingSubmit = true;
    render();

    const payload = {
      wine_id: wineId,
      rating_1_5: rating,
      comment: state.ratingForm.comment || null,
      tried_at: state.ratingForm.tried_at ? new Date(state.ratingForm.tried_at).toISOString() : null,
    };
    try {
      await api("/ratings", { method: "POST", body: JSON.stringify(payload) });
      setStatus("status-fresh", t("ratingSuccess"));
      state.ratingForm.comment = "";
      await loadTriedWines();
    } catch (error) {
      setStatus("status-error", String(error.message || error));
    } finally {
      state.loading.ratingSubmit = false;
      render();
    }
  }

  async function deleteRating(ratingId) {
    if (!state.token) {
      setStatus("status-error", t("authRequired"));
      return;
    }
    if (!window.confirm(t("deleteConfirm"))) {
      return;
    }
    try {
      await api(`/ratings/${ratingId}`, { method: "DELETE" });
      await loadTriedWines();
      setStatus("status-fresh", t("ratingDeleted"));
    } catch (error) {
      setStatus("status-error", String(error.message || error));
    }
  }

  async function loadRouteData() {
    if (state.route === "/") {
      await Promise.all([loadRecommendations("recommended_buys"), loadRecommendations("cheapest_favorites")]);
      await loadRunInfo();
      return;
    }
    if (state.route === "/tried") {
      await loadTriedWines();
      return;
    }
    if (state.route === "/settings") {
      await loadRunInfo();
    }
  }

  function bindEvents() {
    window.addEventListener("popstate", () => {
      state.route = normalizeRoute(window.location.pathname);
      render();
      void loadRouteData();
    });

    document.addEventListener("click", (event) => {
      const target = event.target.closest("[data-action]");
      if (!target) return;

      const action = target.getAttribute("data-action");
      if (action === "route") {
        event.preventDefault();
        const path = target.getAttribute("data-route") || "/";
        navigate(path);
        return;
      }

      if (action === "login") {
        void (async () => {
          try {
            const passwordInput = document.getElementById("passwordInput");
            const payload = {
              user_id: state.activeUser,
              password: passwordInput ? passwordInput.value : state.loginPassword,
            };
            state.loginPassword = payload.password;
            const result = await api("/auth/login", {
              method: "POST",
              body: JSON.stringify(payload),
            });
            state.token = result.access_token;
            saveSession();
            await loadMe();
            await loadUserSettings();
            await loadRouteData();
            await loadHealth();
            render();
          } catch (error) {
            setStatus("status-error", `${t("loginFailed")} ${String(error.message || error)}`);
          }
        })();
        return;
      }

      if (action === "logout") {
        state.token = "";
        state.me = null;
        saveSession();
        setStatus("status-no_data", t("notLoggedIn"));
        render();
        return;
      }

      if (action === "refresh-health") {
        void loadHealth();
        return;
      }

      if (action === "trigger-run") {
        void triggerRun();
        return;
      }

      if (action === "save-user-settings") {
        void saveUserSettings();
        return;
      }

      if (action === "search-tried") {
        const queryInput = document.getElementById("queryInput");
        const wineTypeInput = document.getElementById("wineTypeInput");
        const grapeInput = document.getElementById("grapeInput");
        state.triedFilters.query = queryInput ? queryInput.value.trim() : "";
        state.triedFilters.wine_type = wineTypeInput ? wineTypeInput.value : "";
        state.triedFilters.grape = grapeInput ? grapeInput.value.trim() : "";
        void loadTriedWines();
        return;
      }

      if (action === "clear-tried") {
        state.triedFilters = { query: "", wine_type: "", grape: "" };
        state.selectedWineId = null;
        render();
        void loadTriedWines();
        return;
      }

      if (action === "select-wine") {
        const wineId = Number(target.getAttribute("data-wine-id"));
        state.selectedWineId = Number.isFinite(wineId) ? wineId : null;
        render();
        return;
      }

      if (action === "delete-rating") {
        const ratingId = Number(target.getAttribute("data-rating-id"));
        if (Number.isFinite(ratingId)) {
          void deleteRating(ratingId);
        }
        return;
      }

      if (action === "reload-settings") {
        void loadRunInfo();
      }
    });

    document.addEventListener("change", (event) => {
      const target = event.target;
      if (!(target instanceof HTMLElement)) return;
      if (target.id === "activeUserSelect") {
        const next = target.value === "B" ? "B" : "A";
        if (state.me && state.me.id !== next) {
          state.token = "";
          state.me = null;
          setStatus("status-no_data", t("authRequired"));
        }
        state.activeUser = next;
        state.loginPassword = defaultPassword(next);
        saveSession();
        render();
        return;
      }
      if (target.id === "localeSelect") {
        state.locale = target.value === "ru" ? "ru" : "en";
        saveSession();
        render();
        return;
      }
      if (target.id === "runModeInput") {
        state.runMode = target.value;
        return;
      }
      if (target.id === "passwordInput") {
        state.loginPassword = target.value;
        return;
      }
    });

    document.addEventListener("submit", (event) => {
      const target = event.target;
      if (!(target instanceof HTMLFormElement)) return;
      if (target.id !== "ratingForm") return;
      event.preventDefault();
      const wineIdInput = document.getElementById("wineIdInput");
      const ratingInput = document.getElementById("ratingInput");
      const commentInput = document.getElementById("commentInput");
      const triedAtInput = document.getElementById("triedAtInput");
      state.ratingForm.wine_id = wineIdInput ? wineIdInput.value : "";
      state.ratingForm.rating_1_5 = ratingInput ? ratingInput.value : "4";
      state.ratingForm.comment = commentInput ? commentInput.value : "";
      state.ratingForm.tried_at = triedAtInput ? triedAtInput.value : "";
      void submitRating();
    });
  }

  async function init() {
    bindEvents();
    render();
    if (state.token) {
      await loadMe();
      await loadUserSettings();
    }
    await loadHealth();
    await loadRouteData();
    render();
  }

  void init();
})();
