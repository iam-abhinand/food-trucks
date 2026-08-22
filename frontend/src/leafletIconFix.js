/**
 * Leaflet's default marker icons reference image paths that don't resolve
 * correctly when bundled by Vite/Webpack. This explicitly points Leaflet
 * at the correct icon URLs, pulled from the installed leaflet package itself.
 */
import L from "leaflet";
import icon from "leaflet/dist/images/marker-icon.png";
import iconShadow from "leaflet/dist/images/marker-shadow.png";

delete L.Icon.Default.prototype._getIconUrl;

L.Icon.Default.mergeOptions({
  iconUrl: icon,
  shadowUrl: iconShadow,
});