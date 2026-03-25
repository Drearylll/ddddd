// 在浏览器控制台执行以下代码，清除头像相关的 localStorage 数据

localStorage.removeItem('goIn_gender');
localStorage.removeItem('goIn_face_photo');
localStorage.removeItem('goIn_face_avatar');
localStorage.removeItem('goIn_user_id');

console.log('✅ 已清除所有头像相关的 localStorage 数据');
console.log('刷新页面后将显示空白，可以重新上传照片');
