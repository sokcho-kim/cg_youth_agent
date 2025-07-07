// document.addEventListener('click', async function (e) {
//     const link = e.target.closest('a');
//     if (!link || !link.href.startsWith("https://youth.seoul.go.kr/")) return;

//     e.preventDefault();
//     const originalUrl = link.href;

//     try {
//         const response = await fetch(originalUrl, {
//             method: 'GET',
//             redirect: 'follow',
//             mode: 'cors'
//         });

//         const finalUrl = response.url;

//         if (finalUrl.includes("/index.do")) {
//             // 첫 시도 실패 → 재시도
//             setTimeout(() => {
//                 window.open(originalUrl, "_blank");
//             }, 100);
//         } else {
//             window.open(originalUrl, "_blank");
//         }
//     } catch (err) {
//         window.open(originalUrl, "_blank");
//     }
// });

document.addEventListener('click', function (e) {
    const link = e.target.closest('a');
    if (!link || !link.href.startsWith("https://youth.seoul.go.kr/")) return;

    const originalUrl = link.href;
    const encoded = encodeURIComponent(originalUrl);
    const redirectUrl = `/redirect.html?target=${encoded}`;

    // 새 탭에서 열기
    window.open(redirectUrl, "_blank");

    // 기본 동작 막기
    e.preventDefault();
});
