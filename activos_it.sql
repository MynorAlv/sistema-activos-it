-- Creamos la base de datos si no existe y le decimos a MySQL que la use
CREATE DATABASE IF NOT EXISTS activos_it;
USE activos_it;

-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 08-08-2026 a las 03:04:55
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `equipos`
--

CREATE TABLE `equipos` (
  `id` int(11) NOT NULL,
  `tipo` varchar(100) NOT NULL,
  `caracteristica` varchar(200) NOT NULL,
  `propietario` varchar(100) DEFAULT NULL,
  `ubicacion` varchar(150) DEFAULT NULL,
  `area_responsable` varchar(150) DEFAULT NULL,
  `tipo_informacion` varchar(150) DEFAULT NULL,
  `dependencias` text DEFAULT NULL,
  `sistema_operativo` varchar(100) DEFAULT NULL,
  `version` varchar(100) DEFAULT NULL,
  `ip` varchar(45) DEFAULT NULL,
  `hostname` varchar(100) DEFAULT NULL,
  `ambiente` varchar(50) DEFAULT NULL,
  `estado` varchar(50) DEFAULT NULL,
  `fecha_revision` datetime DEFAULT NULL,
  `fecha_creacion` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `equipos`
--

INSERT INTO `equipos` (`id`, `tipo`, `caracteristica`, `propietario`, `ubicacion`, `area_responsable`, `tipo_informacion`, `dependencias`, `sistema_operativo`, `version`, `ip`, `hostname`, `ambiente`, `estado`, `fecha_revision`, `fecha_creacion`) VALUES
(1, 'Windows Server', '2016', 'TI', 'Nicaragua', 'UWF', 'SERVIDOR AD', 'AD', '1607', '10.0.14393', '147.167.133.23/23', 'FG-23GTS5IX', 'Disaster Recovery', 'Activo', '2026-04-07 00:00:00', '2026-08-07 22:09:21'),
(2, 'FortiGate', '30g', 'Infraestructura', 'Brasil', 'NOC', 'Firewall', 'TIGO ROUTER', 'FortiOS', '7.2', '147.167.133.22/23', 'FG-56DTY7U8', 'Desarrollo', 'Activo', '2026-03-25 00:00:00', '2026-08-07 22:56:24'),
(3, 'FortiGate', '30E-3G4G-NAM', 'GTJM', 'Guatemala', 'Local IT', 'Firewall GT', 'TIGO ROUTER', 'FortiOS FGT_30E_MN', '5.4', '147.167.133.21/23', 'FG-3D4FR2W', 'Producción', NULL, '2021-02-02 00:00:00', '2026-08-07 23:47:52');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios`
--

CREATE TABLE `usuarios` (
  `id` int(11) NOT NULL,
  `usuario` varchar(50) NOT NULL,
  `nombre1` varchar(50) NOT NULL,
  `nombre2` varchar(50) DEFAULT NULL,
  `apellido1` varchar(50) NOT NULL,
  `apellido2` varchar(50) DEFAULT NULL,
  `rol` varchar(50) NOT NULL,
  `puesto` varchar(100) DEFAULT NULL,
  `contrasena` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `usuarios`
--

INSERT INTO `usuarios` (`id`, `usuario`, `nombre1`, `nombre2`, `apellido1`, `apellido2`, `rol`, `puesto`, `contrasena`) VALUES
(1, 'admin', 'Administrador', '', 'Sistema', '', 'Administrador', 'Administrador del Sistema', ''),
(2, 'jperez', 'Juan', 'Carlos', 'Pérez', 'Gómez', 'Ing Nivel 1', 'Ingeniero de Seguridad', ''),
(3, 'mlopez', 'María', 'Elena', 'López', 'Martínez', 'Ing Nivel 2', 'Ingeniero Senior', ''),
(4, 'crodriguez', 'Carlos', 'Andrés', 'Rodríguez', 'García', 'Ing Nivel 3', 'Ingeniero Principal', ''),
(5, 'afernandez', 'Ana', 'María', 'Fernández', 'Reyes', 'Ing Nivel 1', 'Ingeniero de Infraestructura', '');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `vulnerabilidades`
--

CREATE TABLE `vulnerabilidades` (
  `id` int(11) NOT NULL,
  `id_equipo` int(11) NOT NULL,
  `descripcion` text NOT NULL,
  `completada` tinyint(1) DEFAULT NULL,
  `fecha_creacion` datetime DEFAULT NULL,
  `fecha_completada` datetime DEFAULT NULL,
  `codigo` varchar(50) DEFAULT NULL,
  `criticidad` varchar(20) DEFAULT NULL,
  `impacto` text DEFAULT NULL,
  `plan_remediacion` text DEFAULT NULL,
  `tiempo_estimado` varchar(50) DEFAULT NULL,
  `responsable` varchar(100) DEFAULT NULL,
  `fecha_objetivo` datetime DEFAULT NULL,
  `prioridad_remediacion` varchar(50) DEFAULT NULL,
  `observaciones` text DEFAULT NULL,
  `evidencia` varchar(250) DEFAULT NULL,
  `porcentaje_avance` int(11) DEFAULT NULL,
  `riesgo_residual` varchar(50) DEFAULT NULL,
  `estado_remediacion` varchar(50) DEFAULT 'Pendiente',
  `historial_cambios` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`historial_cambios`)),
  `datos_completos` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`datos_completos`))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `vulnerabilidades`
--

INSERT INTO `vulnerabilidades` (`id`, `id_equipo`, `descripcion`, `completada`, `fecha_creacion`, `fecha_completada`, `codigo`, `criticidad`, `impacto`, `plan_remediacion`, `tiempo_estimado`, `responsable`, `fecha_objetivo`, `prioridad_remediacion`, `observaciones`, `evidencia`, `porcentaje_avance`, `riesgo_residual`, `estado_remediacion`, `historial_cambios`, `datos_completos`) VALUES
(1, 1, 'Vulnerabilidad de ejecución remota de código en el componente RDP (Remote Desktop Protocol) de Windows, conocida como \'BlueKeep\'. Permite a un atacante no autenticado ejecutar código arbitrario en el sistema afectado.', 1, '2026-08-07 22:09:37', '2026-08-07 23:24:23', 'CVE-2019-0708', 'Altass', 'Un atacante podría aprovechar esta vulnerabilidad para ejecutar código malicioso en el servidor, lo que podría llevar a la toma de control del sistema, robo de datos o distribución de malware.', 'Aplicar la actualización de seguridad proporcionada por Microsoft (KB4499180) e inhabilitar el servicio RDP si no es necesario. Además, considerar la implementación de soluciones de detección y prevención de intrusiones para monitorear el tráfico de red.', '30 minutos a 2 horas', 'Gerson Canales', '2026-08-15 00:00:00', 'Alta', 'validar porfa', 'test', 0, 'Medio', 'Completada', '[{\"fecha\": \"2026-08-07T22:11:38.620378\", \"usuario\": \"Usuario\", \"accion\": \"Actualización de remediación\", \"datos\": {\"estado_remediacion\": \"Pendiente\", \"responsable\": \"Gerson Canales\", \"fecha_objetivo\": \"2026-08-15\", \"prioridad_remediacion\": \"Alta\", \"observaciones\": \"validar porfa\", \"evidencia\": \"test\", \"porcentaje_avance\": 0, \"riesgo_residual\": \"Medio\", \"comentario\": \"testssss\"}}]', '{\"codigo\": \"CVE-2019-0708\", \"descripcion\": \"Vulnerabilidad de ejecución remota de código en el componente RDP (Remote Desktop Protocol) de Windows, conocida como \'BlueKeep\'. Permite a un atacante no autenticado ejecutar código arbitrario en el sistema afectado.\", \"criticidad\": \"Alta\", \"impacto\": \"Un atacante podría aprovechar esta vulnerabilidad para ejecutar código malicioso en el servidor, lo que podría llevar a la toma de control del sistema, robo de datos o distribución de malware.\", \"recomendacion\": \"Aplicar la actualización de seguridad proporcionada por Microsoft (KB4499180) e inhabilitar el servicio RDP si no es necesario. Además, considerar la implementación de soluciones de detección y prevención de intrusiones para monitorear el tráfico de red.\", \"tiempo_estimado\": \"30 minutos a 2 horas, dependiendo de la complejidad de la infraestructura y la experiencia del administrador\"}'),
(2, 1, 'Vulnerabilidad de ejecución remota de código en el servicio DNS del sistema operativo Windows Server 2016, que permite a un atacante ejecutar código arbitrario en el servidor', 1, '2026-08-07 22:13:49', '2026-08-07 23:16:59', 'CVE-2020-1350', 'Alta11', 'Un atacante podría aprovechar esta vulnerabilidad para obtener acceso no autorizado al servidor y realizar acciones maliciosas, como robar información confidencial o instalar malware', 'Aplicar la actualización de seguridad proporcionada por Microsoft, que corrige la vulnerabilidad y evita la ejecución remota de código', '30 minutos', 'Carlos Andrés Rodríguez García', '2026-08-07 00:00:00', 'Alta', 'Se instalo el parche', 'revisar drive', 100, 'Ninguno', 'Completada', '[{\"fecha\": \"2026-08-07T22:31:04.347364\", \"usuario\": \"Usuario\", \"accion\": \"Actualización de remediación\", \"datos\": {\"estado_remediacion\": \"Completada\", \"responsable\": \"Carlos Andrés Rodríguez García\", \"fecha_objetivo\": \"2026-08-07\", \"prioridad_remediacion\": \"Alta\", \"observaciones\": \"Se instalo el parche\", \"evidencia\": \"revisar drive\", \"porcentaje_avance\": 100, \"riesgo_residual\": \"Ninguno\", \"comentario\": \"Se instalo el parche sin problemas\"}}]', '{\"codigo\": \"CVE-2020-1350\", \"descripcion\": \"Vulnerabilidad de ejecución remota de código en el servicio DNS del sistema operativo Windows Server 2016, que permite a un atacante ejecutar código arbitrario en el servidor\", \"criticidad\": \"Alta\", \"impacto\": \"Un atacante podría aprovechar esta vulnerabilidad para obtener acceso no autorizado al servidor y realizar acciones maliciosas, como robar información confidencial o instalar malware\", \"recomendacion\": \"Aplicar la actualización de seguridad proporcionada por Microsoft, que corrige la vulnerabilidad y evita la ejecución remota de código\", \"tiempo_estimado\": \"30 minutos\"}'),
(3, 2, 'Vulnerabilidad de ejecución remota de código en el servicio HTTP de FortiGate, que permite a un atacante no autenticado ejecutar código arbitrario en el sistema', 1, '2026-08-07 22:56:38', '2026-08-07 23:38:22', 'CVE-2022-26188', 'Media', 'Un atacante podría aprovechar esta vulnerabilidad para obtener acceso no autorizado al sistema, robar información confidencial, instalar malware o realizar otras acciones maliciosas', 'Actualizar el firmware de FortiGate a la versión más reciente, aplicar parches de seguridad y configurar las reglas de firewall para restringir el acceso al servicio HTTP', '2 horas', 'Ana María Fernández Reyes', '2026-08-17 00:00:00', 'Alta', 'se descargo parche', 'https://www.catalog.update.microsoft.com/home.aspx', 84, 'Medio', 'Completada', '[{\"fecha\": \"2026-08-07T23:25:35.809684\", \"usuario\": \"Usuario\", \"accion\": \"Actualización de remediación\", \"datos\": {\"estado_remediacion\": \"En proceso\", \"responsable\": \"Ana María Fernández Reyes\", \"fecha_objetivo\": \"2026-08-17\", \"prioridad_remediacion\": \"Alta\", \"observaciones\": \"dasd\", \"evidencia\": \"asdasd\", \"porcentaje_avance\": 84, \"riesgo_residual\": \"Medio\", \"comentario\": \"asdasd\"}}]', '{\"codigo\": \"CVE-2022-26188\", \"descripcion\": \"Vulnerabilidad de ejecución remota de código en el servicio HTTP de FortiGate, que permite a un atacante no autenticado ejecutar código arbitrario en el sistema\", \"criticidad\": \"Alta\", \"impacto\": \"Un atacante podría aprovechar esta vulnerabilidad para obtener acceso no autorizado al sistema, robar información confidencial, instalar malware o realizar otras acciones maliciosas\", \"recomendacion\": \"Actualizar el firmware de FortiGate a la versión más reciente, aplicar parches de seguridad y configurar las reglas de firewall para restringir el acceso al servicio HTTP\", \"tiempo_estimado\": \"2 horas\"}'),
(4, 2, 'Vulnerabilidad de inyección de comandos en FortiGate que permite a un atacante autenticado ejecutar comandos del sistema operativo en el equipo', 1, '2026-08-07 23:11:10', '2026-08-07 23:12:12', 'CVE-2019-5591', 'Alta', 'Permite a un atacante obtener acceso no autorizado al sistema y llevar a cabo acciones maliciosas', 'Actualizar el firmware a la versión más reciente, restringir el acceso a la consola y limitar los privilegios de los usuarios', '2 horas', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Completada', NULL, '{\"codigo\": \"CVE-2019-5591\", \"descripcion\": \"Vulnerabilidad de inyección de comandos en FortiGate que permite a un atacante autenticado ejecutar comandos del sistema operativo en el equipo\", \"criticidad\": \"Alta\", \"impacto\": \"Permite a un atacante obtener acceso no autorizado al sistema y llevar a cabo acciones maliciosas\", \"recomendacion\": \"Actualizar el firmware a la versión más reciente, restringir el acceso a la consola y limitar los privilegios de los usuarios\", \"tiempo_estimado\": \"2 horas\"}'),
(5, 1, 'La vulnerabilidad de Log4j es un problema de inyección de código remoto que afecta a la biblioteca de registro de Apache Log4j, permitiendo a un atacante ejecutar código arbitrario en el servidor', 0, '2026-08-07 23:48:22', NULL, 'CVE-2021-44228', 'Alta222', 'Un atacante podría aprovechar esta vulnerabilidad para obtener acceso no autorizado, robar datos sensibles o tomar el control del sistema', 'Actualizar la biblioteca Log4j a la versión 2.17.1 o superior, y considerar la implementación de un WAF para monitorear y bloquear tráfico sospechoso', '2 horas', 'Ana María Fernández Reyes', '2026-08-20 00:00:00', 'Alta', 'aplicando parches', 'https://www.catalog.update.microsoft.com/home.aspx', NULL, 'Medio', 'Pendiente', '[{\"fecha\": \"2026-08-08T00:09:19.092455\", \"usuario\": \"Usuario\", \"accion\": \"Actualización de remediación\", \"datos\": {\"estado_remediacion\": \"En proceso\", \"responsable\": \"Ana María Fernández Reyes\", \"fecha_objetivo\": \"2026-08-20\", \"prioridad_remediacion\": \"Alta\", \"observaciones\": \"dasda\", \"evidencia\": \"https://www.catalog.update.microsoft.com/home.aspx\", \"riesgo_residual\": \"Medio\"}}]', '{\"codigo\": \"CVE-2021-44228\", \"descripcion\": \"La vulnerabilidad de Log4j es un problema de inyección de código remoto que afecta a la biblioteca de registro de Apache Log4j, permitiendo a un atacante ejecutar código arbitrario en el servidor\", \"criticidad\": \"Alta\", \"impacto\": \"Un atacante podría aprovechar esta vulnerabilidad para obtener acceso no autorizado, robar datos sensibles o tomar el control del sistema\", \"recomendacion\": \"Actualizar la biblioteca Log4j a la versión 2.17.1 o superior, y considerar la implementación de un WAF para monitorear y bloquear tráfico sospechoso\", \"tiempo_estimado\": \"2 horas\"}');

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `equipos`
--
ALTER TABLE `equipos`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `usuario` (`usuario`);

--
-- Indices de la tabla `vulnerabilidades`
--
ALTER TABLE `vulnerabilidades`
  ADD PRIMARY KEY (`id`),
  ADD KEY `id_equipo` (`id_equipo`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `equipos`
--
ALTER TABLE `equipos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT de la tabla `vulnerabilidades`
--
ALTER TABLE `vulnerabilidades`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `vulnerabilidades`
--
ALTER TABLE `vulnerabilidades`
  ADD CONSTRAINT `vulnerabilidades_ibfk_1` FOREIGN KEY (`id_equipo`) REFERENCES `equipos` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;