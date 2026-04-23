const { execSync } = require('child_process');
const path = require('path');

exports.default = async function(context) {
  const appPath = path.join(context.appOutDir, `${context.packager.appInfo.productName}.app`);
  console.log(`Stripping xattr from ${appPath}`);
  try {
    execSync(`xattr -cr "${appPath}"`, { stdio: 'inherit' });
  } catch (e) {
    console.warn('xattr warning:', e.message);
  }
};
