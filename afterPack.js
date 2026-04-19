const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

exports.default = async function(context) {
  const appPath = path.join(context.appOutDir, `${context.packager.appInfo.productName}.app`);
  const frameworksPath = path.join(appPath, 'Contents', 'Frameworks');
  
  console.log(`Stripping xattr from ${appPath}`);
  
  // Strip the main app
  try { execSync(`xattr -cr "${appPath}"`, { stdio: 'inherit' }); } 
  catch (e) { console.warn('main app:', e.message); }

  // Strip each helper app inside Frameworks individually
  if (fs.existsSync(frameworksPath)) {
    const entries = fs.readdirSync(frameworksPath);
    for (const entry of entries) {
      const fullPath = path.join(frameworksPath, entry);
      try { execSync(`xattr -cr "${fullPath}"`, { stdio: 'inherit' }); }
      catch (e) { console.warn(`${entry}:`, e.message); }
      
      if (entry.endsWith('.app')) {
        const macosPath = path.join(fullPath, 'Contents', 'MacOS');
        if (fs.existsSync(macosPath)) {
          const binaries = fs.readdirSync(macosPath);
          for (const bin of binaries) {
            const binPath = path.join(macosPath, bin);
            try { execSync(`xattr -cr "${binPath}"`, { stdio: 'inherit' }); }
            catch (e) { console.warn(`binary ${bin}:`, e.message); }
            try { execSync(`dot_clean "${binPath}"`, { stdio: 'inherit' }); }
            catch (e) {}
          }
        }
      }
    }
  }

  // dot_clean the entire bundle
  try { 
    execSync(`dot_clean -m "${appPath}"`, { stdio: 'inherit' });
    console.log('dot_clean complete');
  } catch (e) { console.warn('dot_clean:', e.message); }
};
