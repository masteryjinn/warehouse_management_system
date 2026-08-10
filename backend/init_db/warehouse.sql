-- MySQL dump 10.13  Distrib 8.0.41, for Win64 (x86_64)
--
-- Host: localhost    Database: WarehouseDB
-- ------------------------------------------------------
-- Server version	8.0.41

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `contacts_customers`
--

DROP TABLE IF EXISTS `contacts_customers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `contacts_customers` (
  `contact_id` int NOT NULL AUTO_INCREMENT,
  `customer_id` int NOT NULL,
  `contact_type` varchar(50) NOT NULL,
  `contact_value` varchar(255) NOT NULL,
  PRIMARY KEY (`contact_id`),
  UNIQUE KEY `unique_customer_contact` (`customer_id`,`contact_type`,`contact_value`),
  CONSTRAINT `fk_customer_contact` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`customer_id`) ON DELETE CASCADE,
  CONSTRAINT `contacts_customers_chk_1` CHECK ((`contact_type` in (_utf8mb4'address',_utf8mb4'phone',_utf8mb4'email')))
) ENGINE=InnoDB AUTO_INCREMENT=11901 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `contacts_customers`
--

LOCK TABLES `contacts_customers` WRITE;
/*!40000 ALTER TABLE `contacts_customers` DISABLE KEYS */;
INSERT INTO `contacts_customers` VALUES (10954,1,'address','сквер Ветеранів праці, буд. 9 кв. 59, Болград, 65409'),(10956,1,'email','feofaniashchuk@example.com'),(10955,1,'phone','+380506118664'),(9697,2,'address','провулок Донецька, буд. 57, Комарно, 51065'),(9699,2,'email','vadymsych@example.org'),(9698,2,'phone','+380974266606'),(10228,3,'address','провулок Бокаріуса, буд. 240, Перемишляни, 51277'),(10230,3,'email','lukian76@example.com'),(10229,3,'phone','+380632722562'),(11101,4,'address','сквер Наявний 1-й, буд. 729, Носівка, 65932'),(11103,4,'email','zynoviiiurchyshyn@example.com'),(11102,4,'phone','+380937291265'),(9298,5,'address','провулок Трудовий, буд. 72, Українськ, 88962'),(9300,5,'email','hordii70@example.org'),(9299,5,'phone','+380672800459'),(10789,6,'address','шосе Ганса Германа, буд. 4 кв. 996, Тиврів, 16546'),(10791,6,'email','volodymyrapavlenko@example.org'),(10790,6,'phone','+380678546121'),(7546,7,'address','узвіз Матюшенка, буд. 2, Шумськ, 52811'),(7548,7,'email','yiaremko@example.net'),(7547,7,'phone','+380635917175'),(11389,8,'address','сквер Івахненка Петра, буд. 2 кв. 46, Ізяслав, 05953'),(11391,8,'email','qchalenko@example.org'),(11390,8,'phone','+380678234068'),(9601,9,'address','площа Небесної Сотні, буд. 071 кв. 915, Новогродівка, 99882'),(9603,9,'email','yfranko@example.org'),(9602,9,'phone','+380932972144'),(9712,10,'address','вулиця Картамишевський, буд. 65 кв. 173, Синельникове, 63656'),(9714,10,'email','oriabchenko@example.com'),(9713,10,'phone','+380679316227'),(10366,11,'address','парк Лютеранський, буд. 61, Кременець, 66377'),(10368,11,'email','verkhovynetsarsen@example.net'),(10367,11,'phone','+380631248829'),(11752,12,'address','вулиця Флотський 1-й, буд. 14, Коростишів, 10476'),(11754,12,'email','aleksiukorest@example.net'),(11753,12,'phone','+380501692959'),(10588,13,'address','шосе Нафтовиків, буд. 15 кв. 3, Яремче, 45083'),(10590,13,'email','uhrechkore234@example.net'),(10589,13,'phone','+380508224704'),(10603,14,'address','проспект Грузинська, буд. 50 кв. 2, Умань, 02263'),(10605,14,'email','kanivetsvalentyna@example.org'),(10604,14,'phone','+380671029918'),(6550,15,'address','проспект Василя Кандинського, буд. 18 кв. 7, Кременчук, 66937'),(6552,15,'email','irenakybkalo@example.com'),(6551,15,'phone','+380972427165'),(10099,16,'address','узвіз Діхтієвського Віктора, буд. 528 кв. 8, Рівне, 24146'),(10101,16,'email','hermanhabelko@example.com'),(10100,16,'phone','+380673608874'),(11650,17,'address','вулиця Котляревського, буд. 54, Снятин, 92806'),(11652,17,'email','lesmatiash@example.org'),(11651,17,'phone','+380938252609'),(11317,18,'address','шосе Супутників, буд. 21 кв. 10, Феодосія, 90003'),(11319,18,'email','leonfilipenko@example.org'),(11318,18,'phone','+380672466076'),(7600,19,'address','сквер Лузанівський 2-й, буд. 01 кв. 9, Василівка, 11259'),(7602,19,'email','stkach@example.org'),(7601,19,'phone','+380509581843'),(10795,20,'address','вулиця Героїв Небесної Сотні, буд. 68, Добропілля, 77252'),(10797,20,'email','nvakarchuk@example.net'),(10796,20,'phone','+380679107039');
/*!40000 ALTER TABLE `contacts_customers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `contacts_employees`
--

DROP TABLE IF EXISTS `contacts_employees`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `contacts_employees` (
  `contact_id` int NOT NULL AUTO_INCREMENT,
  `employee_id` int NOT NULL,
  `contact_type` varchar(50) NOT NULL,
  `contact_value` varchar(255) NOT NULL,
  PRIMARY KEY (`contact_id`),
  UNIQUE KEY `unique_employee_contact` (`employee_id`,`contact_type`,`contact_value`),
  CONSTRAINT `fk_employee_contact` FOREIGN KEY (`employee_id`) REFERENCES `employees` (`employee_id`) ON DELETE CASCADE,
  CONSTRAINT `contacts_employees_chk_1` CHECK ((`contact_type` in (_utf8mb4'address',_utf8mb4'phone',_utf8mb4'email')))
) ENGINE=InnoDB AUTO_INCREMENT=16686 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `contacts_employees`
--

LOCK TABLES `contacts_employees` WRITE;
/*!40000 ALTER TABLE `contacts_employees` DISABLE KEYS */;
INSERT INTO `contacts_employees` VALUES (10485,8,'address','набережна Флотська, буд. 95, Верхньодніпровськ, 33857'),(10487,8,'email','ldashenko_ua@example.org'),(10486,8,'phone','+380967332299'),(12312,21,'address','набережна Трамвайна, буд. 1 кв. 86, Звенигородка, 72177'),(12314,21,'email','babiistefan@example.com'),(12313,21,'phone','+380984848848'),(10929,22,'address','площа Круговий, буд. 4 кв. 714, Ічня, 02281'),(10931,22,'email','tetiana68@example.com'),(10930,22,'phone','+380246771586'),(11673,23,'address','площа Нафтовиків 3-й, буд. 495 кв. 2, Сокаль, 24037'),(11675,23,'email','klavdiiashtepa@example.org'),(11674,23,'phone','+380937478908'),(14835,24,'address','парк Сонячна, буд. 330, Роздільна, 04247'),(14837,24,'email','eduardandroshchuk@example.com'),(14836,24,'phone','+380254486844'),(9960,25,'address','вулиця Глиняна, буд. 327, Мена, 12293'),(9962,25,'email','orysiaiaremenko@example.net'),(9961,25,'phone','+380019192386'),(10293,26,'address','шосе Леся Курбаса, буд. 741 кв. 1, Чорнобиль, 29119'),(10295,26,'email','kamillavyshyvana@example.com'),(10294,26,'phone','+380976665056'),(9360,27,'address','проспект Одеса-Головна, буд. 687 кв. 92, Підгайці, 80732'),(9362,27,'email','tsiutsiuraedyta@example.net'),(9361,27,'phone','+386802352768'),(10539,28,'address','парк Зоряна, буд. 92, Новомиргород, 06029'),(10541,28,'email','emiliiaabramenko@example.net'),(10540,28,'phone','+385029790987'),(8442,29,'address','провулок Кільцева, буд. 854 кв. 824, Нетішин, 30529'),(8444,29,'email','chernenkoopanas@example.com'),(8443,29,'phone','+380733924512'),(9816,31,'address','узвіз Лазурний 1-й, буд. 370, Глухів, 96677'),(9818,31,'email','volodymyraivanchenko@example.net'),(9817,31,'phone','+380751439720'),(10716,35,'address','площа Флотська, буд. 2, Верхньодніпровськ, 49335'),(10718,35,'email','ihnat06@example.net'),(10717,35,'phone','+380050047437'),(9003,36,'address','парк Овідіопольська дорога, буд. 2 кв. 04, Збараж, 38270'),(9005,36,'email','spoltavets@example.com'),(9004,36,'phone','+380950481419'),(12894,39,'address','вулиця Обільний 1-й, буд. 8, Ялта, 27346'),(12896,39,'email','maryna25@example.org'),(12895,39,'phone','+380921535155'),(16685,4031,'address','вул. Різдвяна, буд. 115, кв. 90, Черкаси, 18003'),(16683,4031,'email','irynaost95@gmail.com'),(16684,4031,'phone','+380937711096');
/*!40000 ALTER TABLE `contacts_employees` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `contacts_suppliers`
--

DROP TABLE IF EXISTS `contacts_suppliers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `contacts_suppliers` (
  `contact_id` int NOT NULL AUTO_INCREMENT,
  `supplier_id` int NOT NULL,
  `contact_type` varchar(50) NOT NULL,
  `contact_value` varchar(255) NOT NULL,
  PRIMARY KEY (`contact_id`),
  UNIQUE KEY `unique_supplier_contact` (`supplier_id`,`contact_type`,`contact_value`),
  CONSTRAINT `fk_supplier_contact` FOREIGN KEY (`supplier_id`) REFERENCES `suppliers` (`supplier_id`) ON DELETE CASCADE,
  CONSTRAINT `contacts_suppliers_chk_1` CHECK ((`contact_type` in (_utf8mb4'address',_utf8mb4'phone',_utf8mb4'email')))
) ENGINE=InnoDB AUTO_INCREMENT=11584 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `contacts_suppliers`
--

LOCK TABLES `contacts_suppliers` WRITE;
/*!40000 ALTER TABLE `contacts_suppliers` DISABLE KEYS */;
INSERT INTO `contacts_suppliers` VALUES (8587,1,'address','сквер Юннатів 3-й, буд. 298, Нова Одеса, 17265'),(8589,1,'email','ezinkevych@example.org'),(8588,1,'phone','+380505115463'),(7837,2,'address','вулиця Кривобалківська, буд. 36, Моршин, 98801'),(7839,2,'email','vladyslavvashchuk@example.net'),(7838,2,'phone','+380975670182'),(7585,3,'address','вулиця Василя Кандинського, буд. 44, Луганськ, 17044'),(7587,3,'email','kizhakevych@example.org'),(7586,3,'phone','+380936058728'),(6091,4,'address','шосе 9-та Лінія Дачі Ковалевського, буд. 009 кв. 876, Вараш, 81318'),(6093,4,'email','baidastanislav@example.com'),(6092,4,'phone','+380933725480'),(10195,5,'address','проспект Стражеска Миколи, буд. 392, Зимогір\'я, 51421'),(10197,5,'email','holykolha@example.org'),(10196,5,'phone','+380639174683'),(7648,6,'address','узвіз 18-та Лінія 6-й ст. Люстдорфської дороги, буд. 870, Ізюм, 71401'),(7650,6,'email','edyta345@example.com'),(7649,6,'phone','+380936010459'),(8332,7,'address','шосе Панаса Саксаганського, буд. 18 кв. 02, Бучач, 72057'),(8334,7,'email','irynabandura@example.org'),(8333,7,'phone','+380508639321'),(7144,8,'address','набережна Танкістів, буд. 22, Великі Мости, 87121'),(7146,8,'email','nandriievych@example.org'),(7145,8,'phone','+380939161941'),(7537,9,'address','сквер 5-та Лінія 6-й ст. Люстдорфської дороги, буд. 60, Миколаїв, 91360'),(7539,9,'email','liudmylalavrenko@example.com'),(7538,9,'phone','+380634122821'),(6079,10,'address','проспект Виноградний тупик, буд. 68, Авдіївка, 27232'),(6081,10,'email','frantsbarabash@example.com'),(6080,10,'phone','+380502892742'),(9013,11,'address','парк Миколи Костомарова, буд. 10, Бібрка, 53686'),(9015,11,'email','artympavlo@example.net'),(9014,11,'phone','+380631439920'),(11254,12,'address','парк Балтська дорога, буд. 8 кв. 14, Ананьїв, 76341'),(11256,12,'email','alevtynvalenko@example.org'),(11255,12,'phone','+380937051377'),(9418,13,'address','проспект Місячний, буд. 4, Іловайськ, 41042'),(9420,13,'email','wvovk@example.net'),(9419,13,'phone','+380638319321'),(6289,14,'address','парк Мацієвської узвіз, буд. 46 кв. 581, Ржищів, 30453'),(6291,14,'email','rzharko@example.net'),(6290,14,'phone','+380508749440'),(7246,15,'address','вулиця Планетна, буд. 209, Нова Одеса, 49749'),(7248,15,'email','iurchyshynhalyna@example.org'),(7247,15,'phone','+380935030541'),(7123,16,'address','шосе Прибережний, буд. 592, Корсунь-Шевченківський, 08368'),(7125,16,'email','zdashenko@example.net'),(7124,16,'phone','+380931782928'),(10849,17,'address','набережна Нова, буд. 80, Копичинці, 27077'),(10851,17,'email','nestaikohanna@example.com'),(10850,17,'phone','+380632348606'),(7045,18,'address','провулок Контрадмірала Остроградського, буд. 5 кв. 2, Валки, 72393'),(7047,18,'email','teodor71@example.net'),(7046,18,'phone','+380933745966'),(9913,19,'address','шосе 5-та Лінія 6-й ст. Люстдорфської дороги, буд. 598, Прилуки, 17571'),(9915,19,'email','dankevychpanas@example.org'),(9914,19,'phone','+380971107819'),(6619,20,'address','набережна Василя Фащенка, буд. 9 кв. 17, Сватове, 40373'),(6621,20,'email','vitalii10@example.com'),(6620,20,'phone','+380976710048');
/*!40000 ALTER TABLE `contacts_suppliers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `customers`
--

DROP TABLE IF EXISTS `customers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `customers` (
  `customer_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `type` varchar(50) NOT NULL,
  PRIMARY KEY (`customer_id`),
  UNIQUE KEY `name` (`name`),
  CONSTRAINT `customers_chk_1` CHECK ((`type` in (_utf8mb4'individual',_utf8mb4'business')))
) ENGINE=InnoDB AUTO_INCREMENT=2008 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `customers`
--

LOCK TABLES `customers` WRITE;
/*!40000 ALTER TABLE `customers` DISABLE KEYS */;
INSERT INTO `customers` VALUES (1,'Святослава Ейбоженко','individual'),(2,'Олена Литвин','individual'),(3,'пан Франц Данченко','individual'),(4,'Соломія Токар','individual'),(5,'Михайло Семенченко','individual'),(6,'Роман Дашкевич','individual'),(7,'Данна Ємельяненко','business'),(8,'Тимофій Кармалюк','individual'),(9,'Олег Сомко','individual'),(10,'Олесь Вітер','individual'),(11,'пані Єва Дзюба','individual'),(12,'Ярема Ґалаґан','individual'),(13,'Пармен Олійниченко','individual'),(14,'Петро Забара','individual'),(15,'Богданна Рубець','business'),(16,'пан Дмитро Дергач','individual'),(17,'Шиян Гордій Адамович','individual'),(18,'Тереза Ковалюк','business'),(19,'Дарина Сімашкевич','business'),(20,'Роман Ємець','business');
/*!40000 ALTER TABLE `customers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `employees`
--

DROP TABLE IF EXISTS `employees`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `employees` (
  `employee_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `position` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`employee_id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=4032 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `employees`
--

LOCK TABLES `employees` WRITE;
/*!40000 ALTER TABLE `employees` DISABLE KEYS */;
INSERT INTO `employees` VALUES (8,'Давид Левченко','Адміністратор'),(21,'Леопольд Єременко','Комірник'),(22,'Світлана Атрощенко','Електрослюсар'),(23,'Ігор Єрьоменко','Гірничий інженер'),(24,'Пармен Гоголь-Яновський','Драматург'),(25,'Віра Гавришкевич','Нотаріус'),(26,'Геннадій Євдокименко','Педагог'),(27,'Болеслав Бабич','Випробувач'),(28,'Данило Гайдамака','Адвокат'),(29,'Ада Нестайко','Тестер'),(31,'Вишняк Панас Олексович','Парфюмер'),(35,'Демид Терещенко','Менеджер з продажу'),(36,'Антон Мазур','Конструктор'),(39,'Марта Стець','Секретар'),(4031,'Остапенко Ірина ','Розробник ПЗ');
/*!40000 ALTER TABLE `employees` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orderdetails`
--

DROP TABLE IF EXISTS `orderdetails`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orderdetails` (
  `order_detail_id` int NOT NULL AUTO_INCREMENT,
  `order_id` int DEFAULT NULL,
  `product_id` int DEFAULT NULL,
  `quantity` int NOT NULL,
  `price` decimal(10,2) NOT NULL,
  PRIMARY KEY (`order_detail_id`),
  KEY `idx_order_details_order_id` (`order_id`),
  CONSTRAINT `fk_orderdetails_order` FOREIGN KEY (`order_id`) REFERENCES `orders` (`order_id`) ON DELETE CASCADE,
  CONSTRAINT `orderdetails_chk_1` CHECK ((`quantity` > 0))
) ENGINE=InnoDB AUTO_INCREMENT=66 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orderdetails`
--

LOCK TABLES `orderdetails` WRITE;
/*!40000 ALTER TABLE `orderdetails` DISABLE KEYS */;
INSERT INTO `orderdetails` VALUES (1,1,1,1,35000.00),(2,1,2,1,22000.00),(3,1,22,2,2900.00),(4,1,12,2,1100.00),(5,2,3,1,4500.00),(6,2,4,1,6200.00),(7,3,21,2,340.00),(8,3,5,8,450.00),(9,3,18,2,420.00),(10,3,19,5,680.00),(11,4,19,4,680.00),(12,4,17,5,850.00),(13,5,22,3,2900.00),(14,5,20,2,1950.00),(15,6,2,2,22000.00),(16,6,11,5,250.00),(17,7,5,10,450.00),(18,7,18,3,420.00),(19,8,1,1,35000.00),(20,8,22,2,2900.00),(21,9,7,12,650.00),(22,9,8,20,180.00),(23,10,3,2,4500.00),(24,10,4,1,6200.00),(25,11,15,6,540.00),(26,11,21,4,340.00),(27,12,16,15,220.00),(28,12,17,3,850.00),(29,13,9,4,450.00),(30,13,10,5,320.00),(31,14,12,3,1100.00),(32,14,13,1,3800.00),(33,15,14,8,950.00),(34,15,20,2,1950.00),(35,16,2,1,22000.00),(36,16,6,4,1200.00),(37,17,19,2,680.00),(38,17,11,10,250.00),(39,18,1,2,35000.00),(40,19,7,15,650.00),(41,19,21,5,340.00),(42,20,5,25,450.00),(43,20,6,5,1200.00),(44,21,22,4,2900.00),(45,21,14,3,950.00),(46,22,3,3,4500.00),(47,23,15,8,540.00),(48,23,8,15,180.00),(49,24,16,30,220.00),(50,25,12,4,1100.00),(51,25,2,2,22000.00),(52,26,9,5,450.00),(53,26,20,3,1950.00),(54,27,10,10,320.00),(55,27,11,12,250.00),(56,28,13,2,3800.00),(57,28,17,5,850.00),(58,29,18,20,420.00),(59,29,19,1,680.00),(60,30,1,1,35000.00),(61,30,7,6,650.00),(62,31,3,3,4500.00),(63,31,2,4,22000.00),(64,32,4,60,6200.00),(65,32,20,106,1950.00);
/*!40000 ALTER TABLE `orderdetails` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `trg_order_detail_after_insert` AFTER INSERT ON `orderdetails` FOR EACH ROW BEGIN
    UPDATE Products
    SET quantity = quantity - NEW.quantity
    WHERE product_id = NEW.product_id;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `orders`
--

DROP TABLE IF EXISTS `orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orders` (
  `order_id` int NOT NULL AUTO_INCREMENT,
  `customer_id` int DEFAULT NULL,
  `order_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `status` enum('draft','new','collecting','review_pack','packed','shipped','restocking','unpacking','review_restock','cancelled') DEFAULT 'draft',
  PRIMARY KEY (`order_id`),
  KEY `idx_orders_customer_id` (`customer_id`),
  KEY `idx_orders_status_date` (`status`,`order_date`),
  CONSTRAINT `orders_chk_1` CHECK ((`status` in (_utf8mb4'draft',_utf8mb4'new',_utf8mb4'collecting',_utf8mb4'review_pack',_utf8mb4'packed',_utf8mb4'shipped',_utf8mb4'restocking',_utf8mb4'unpacking',_utf8mb4'review_restock',_utf8mb4'cancelled')))
) ENGINE=InnoDB AUTO_INCREMENT=33 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orders`
--

LOCK TABLES `orders` WRITE;
/*!40000 ALTER TABLE `orders` DISABLE KEYS */;
INSERT INTO `orders` VALUES (1,4,'2026-05-16 09:04:21','shipped'),(2,2,'2026-05-16 09:05:29','shipped'),(3,4,'2026-05-16 09:06:00','shipped'),(4,1,'2026-05-16 09:06:52','restocking'),(5,6,'2026-05-16 09:07:26','shipped'),(6,1,'2026-04-18 11:20:00','shipped'),(7,2,'2026-04-20 08:15:00','shipped'),(8,3,'2026-04-21 13:40:00','shipped'),(9,4,'2026-04-23 06:30:00','shipped'),(10,5,'2026-04-24 12:10:00','shipped'),(11,1,'2026-04-26 09:25:00','shipped'),(12,2,'2026-04-27 14:00:00','shipped'),(13,3,'2026-04-29 07:45:00','shipped'),(14,4,'2026-04-30 11:10:00','shipped'),(15,5,'2026-05-02 08:35:00','shipped'),(16,1,'2026-05-03 13:50:00','shipped'),(17,2,'2026-05-04 06:15:00','shipped'),(18,3,'2026-05-06 10:20:00','shipped'),(19,4,'2026-05-07 12:45:00','shipped'),(20,5,'2026-05-08 07:00:00','shipped'),(21,1,'2026-05-10 08:30:00','shipped'),(22,2,'2026-05-11 11:15:00','shipped'),(23,3,'2026-05-12 13:05:00','shipped'),(24,4,'2026-05-13 09:40:00','shipped'),(25,5,'2026-05-13 14:20:00','shipped'),(26,1,'2026-05-14 07:50:00','shipped'),(27,2,'2026-05-14 12:30:00','shipped'),(28,3,'2026-05-15 08:15:00','shipped'),(29,4,'2026-05-15 13:45:00','shipped'),(30,5,'2026-05-16 07:20:00','shipped'),(31,2,'2026-05-16 10:19:49','packed'),(32,4,'2026-05-16 10:29:30','cancelled');
/*!40000 ALTER TABLE `orders` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `log_status_change` AFTER UPDATE ON `orders` FOR EACH ROW BEGIN
    IF OLD.status <> NEW.status THEN
        INSERT INTO OrderStatusHistory (order_id, status, changed_at)
        VALUES (NEW.order_id, NEW.status, CURRENT_TIMESTAMP);
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `orderstatushistory`
--

DROP TABLE IF EXISTS `orderstatushistory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orderstatushistory` (
  `history_id` int NOT NULL AUTO_INCREMENT,
  `order_id` int DEFAULT NULL,
  `status` varchar(50) NOT NULL,
  `changed_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`history_id`),
  CONSTRAINT `orderstatushistory_chk_1` CHECK ((`status` in (_utf8mb4'draft',_utf8mb4'new',_utf8mb4'collecting',_utf8mb4'review_pack',_utf8mb4'packed',_utf8mb4'shipped',_utf8mb4'restocking',_utf8mb4'unpacking',_utf8mb4'review_restock',_utf8mb4'cancelled')))
) ENGINE=InnoDB AUTO_INCREMENT=64 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orderstatushistory`
--

LOCK TABLES `orderstatushistory` WRITE;
/*!40000 ALTER TABLE `orderstatushistory` DISABLE KEYS */;
INSERT INTO `orderstatushistory` VALUES (1,1636,'cancelled','2026-04-22 14:41:25'),(2,1636,'collecting','2026-04-22 14:42:12'),(3,1635,'collecting','2026-04-22 14:42:21'),(6,1636,'review_pack','2026-04-22 14:44:20'),(7,1635,'restocking','2026-04-22 14:49:21'),(8,1636,'packed','2026-04-22 14:49:56'),(9,1636,'shipped','2026-05-11 11:13:37'),(10,1638,'new','2026-05-12 06:33:57'),(11,1638,'collecting','2026-05-12 06:34:48'),(12,1638,'review_pack','2026-05-12 06:35:16'),(13,1635,'unpacking','2026-05-12 06:39:11'),(14,1635,'review_restock','2026-05-12 06:39:19'),(15,1634,'collecting','2026-05-12 06:39:30'),(16,1632,'collecting','2026-05-12 06:39:40'),(17,1633,'collecting','2026-05-12 06:39:47'),(18,1633,'review_pack','2026-05-12 06:39:54'),(19,1632,'review_pack','2026-05-12 06:40:03'),(20,1634,'review_pack','2026-05-12 06:40:10'),(21,1638,'packed','2026-05-12 06:40:53'),(22,1635,'cancelled','2026-05-12 06:42:24'),(23,1634,'packed','2026-05-12 06:42:31'),(24,1633,'packed','2026-05-12 06:43:02'),(25,1632,'packed','2026-05-12 06:43:08'),(26,1632,'shipped','2026-05-12 06:43:50'),(27,1633,'shipped','2026-05-12 06:43:50'),(28,1634,'shipped','2026-05-12 06:43:50'),(29,1638,'shipped','2026-05-12 06:43:59'),(30,1638,'collecting','2026-05-15 14:55:03'),(31,1638,'review_pack','2026-05-15 14:55:11'),(32,1638,'packed','2026-05-15 14:56:39'),(33,1,'new','2026-05-16 09:05:08'),(34,2,'new','2026-05-16 09:05:44'),(35,3,'new','2026-05-16 09:06:37'),(36,4,'new','2026-05-16 09:07:13'),(37,5,'new','2026-05-16 09:07:47'),(38,5,'collecting','2026-05-16 09:15:56'),(39,1,'collecting','2026-05-16 09:16:03'),(40,2,'collecting','2026-05-16 09:16:09'),(41,3,'collecting','2026-05-16 09:16:14'),(42,4,'collecting','2026-05-16 09:16:20'),(43,1,'review_pack','2026-05-16 09:16:28'),(44,2,'review_pack','2026-05-16 09:16:34'),(45,3,'review_pack','2026-05-16 09:16:40'),(46,4,'review_pack','2026-05-16 09:16:46'),(47,5,'review_pack','2026-05-16 09:16:52'),(48,5,'packed','2026-05-16 09:17:55'),(49,4,'restocking','2026-05-16 09:18:46'),(50,3,'packed','2026-05-16 09:19:00'),(51,2,'packed','2026-05-16 09:19:08'),(52,1,'packed','2026-05-16 09:19:15'),(53,1,'shipped','2026-05-16 09:19:31'),(54,2,'shipped','2026-05-16 09:19:31'),(55,3,'shipped','2026-05-16 09:19:31'),(56,5,'shipped','2026-05-16 09:19:41'),(57,31,'new','2026-05-16 10:20:40'),(58,31,'collecting','2026-05-16 10:21:53'),(59,31,'review_pack','2026-05-16 10:22:03'),(61,31,'packed','2026-05-16 10:23:27'),(62,32,'new','2026-05-16 10:30:14'),(63,32,'cancelled','2026-05-16 10:33:44');
/*!40000 ALTER TABLE `orderstatushistory` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `productcategories`
--

DROP TABLE IF EXISTS `productcategories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `productcategories` (
  `category_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  PRIMARY KEY (`category_id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `productcategories`
--

LOCK TABLES `productcategories` WRITE;
/*!40000 ALTER TABLE `productcategories` DISABLE KEYS */;
INSERT INTO `productcategories` VALUES (10,'Автотовари'),(1,'Електроніка'),(9,'Здоров’я та краса'),(12,'Зоотовари'),(8,'Іграшки та ігри'),(4,'Їжа'),(6,'Канцелярія'),(5,'Книги'),(2,'Меблі'),(3,'Одяг'),(7,'Побутова техніка'),(14,'Побутова хімія'),(11,'Сад та інструменти'),(13,'Спорт та туризм'),(15,'Технології');
/*!40000 ALTER TABLE `productcategories` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `products`
--

DROP TABLE IF EXISTS `products`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `products` (
  `product_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `description` text,
  `price` decimal(10,2) NOT NULL,
  `quantity` int NOT NULL,
  `expiration_date` date DEFAULT NULL,
  `category_id` int DEFAULT NULL,
  `supplier_id` int DEFAULT NULL,
  `unit` varchar(20) DEFAULT 'pcs',
  `section_id` int DEFAULT NULL,
  PRIMARY KEY (`product_id`),
  KEY `idx_product_category_supplier` (`category_id`,`supplier_id`),
  CONSTRAINT `products_chk_1` CHECK ((`quantity` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `products`
--

LOCK TABLES `products` WRITE;
/*!40000 ALTER TABLE `products` DISABLE KEYS */;
INSERT INTO `products` VALUES (1,'Ноутбук Pro 15','Потужний ноутбук для роботи та навчання',35000.00,148,NULL,1,1,'шт',5),(2,'Смартфон X10','Флагманський smartphone із чудовою камерою',22000.00,195,NULL,1,1,'шт',5),(3,'Крісло офісне','Ергономічне крісло з регулюванням висоти',4500.00,76,NULL,2,2,'шт',7),(4,'Стіл письмовий','Сучасний мінімалістичний стіл з дерева',6200.00,63,NULL,2,2,'шт',7),(5,'Футболка бавовняна','Класична однотонна футболка',450.00,467,NULL,3,3,'шт',4),(6,'Худі oversize','Тепле та зручне щоденне худі',1200.00,297,NULL,3,3,'шт',4),(7,'Кава в зернах 1кг','Арабіка середнього обсмаження',650.00,377,'2027-02-22',4,4,'шт',6),(8,'Чай зелений 100г','Високоякісний листовий зелений чай',180.00,580,'2027-04-30',4,4,'шт',6),(9,'Підручник з SQL','Практичний посібник для розробників',450.00,145,NULL,5,5,'шт',2),(10,'Художній роман','Класичне видання в твердій обкладинці',320.00,243,NULL,5,5,'шт',2),(11,'Набір блокнотів','Якісний папір, лінійка, 3 штуки в упаковці',250.00,383,NULL,6,1,'шт',11),(12,'Електрочайник','Швидке закипання, корпус з нержавіючої сталі',1100.00,119,NULL,7,2,'шт',10),(13,'Мікрохвильова піч','Об\'єм 20 літрів, кілька режимів розігріву',3800.00,70,NULL,7,2,'шт',10),(14,'Настільна гра \"Стратегія\"','Захоплива гра для компанії від 2 до 4 гравців',950.00,183,NULL,8,3,'шт',15),(15,'Крем для обличчя','Зволожувальний крем з натуральними компонентами',540.00,338,'2027-05-28',9,4,'шт',9),(16,'Омивач скла 4л','Зимовий омивач із приємним ароматом',220.00,459,'2028-05-12',10,5,'шт',1),(17,'Набір викруток','Професійний набір магнітних викруток (12 шт)',850.00,139,NULL,11,1,'шт',8),(18,'Корм для котів 1.5кг','Збалансований сухий корм для дорослих котів',420.00,431,'2027-01-30',12,2,'шт',12),(19,'Дряпка для котів','Зручна вертикальна дряпка з сизалевою ниткою',680.00,88,NULL,12,2,'шт',12),(20,'Рюкзак туристичний','Місткий рюкзак на 45 літрів для походів',1950.00,107,NULL,13,3,'шт',13),(21,'Гель для прання 2л','Концентрований гель для кольорових речей',340.00,397,'2027-05-30',14,4,'шт',3),(22,'Бездротові навушники','Навушники з активним шумозаглушенням',2900.00,219,NULL,15,5,'шт',14),(23,'Печиво пісочне 1 кг','',150.00,10,'2026-11-12',4,6,'шт',6);
/*!40000 ALTER TABLE `products` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `reports`
--

DROP TABLE IF EXISTS `reports`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `reports` (
  `report_id` int NOT NULL AUTO_INCREMENT,
  `report_type` varchar(255) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`report_id`),
  UNIQUE KEY `report_type` (`report_type`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reports`
--

LOCK TABLES `reports` WRITE;
/*!40000 ALTER TABLE `reports` DISABLE KEYS */;
INSERT INTO `reports` VALUES (1,'32d156e828718e886c9f5b694506e219394794e5f9c8d543ff3b2cf5440df852','2025-07-17 14:02:49');
/*!40000 ALTER TABLE `reports` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `stockmovements`
--

DROP TABLE IF EXISTS `stockmovements`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `stockmovements` (
  `movement_id` int NOT NULL AUTO_INCREMENT,
  `product_id` int NOT NULL,
  `movement_type` varchar(15) NOT NULL,
  `quantity` int NOT NULL,
  `movement_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `from_section_id` int DEFAULT NULL,
  `to_section_id` int DEFAULT NULL,
  `movement_reason` varchar(100) DEFAULT NULL,
  `purchase_price` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`movement_id`),
  KEY `product_id` (`product_id`),
  KEY `from_section_id` (`from_section_id`),
  KEY `to_section_id` (`to_section_id`),
  CONSTRAINT `stockmovements_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`) ON DELETE CASCADE,
  CONSTRAINT `stockmovements_ibfk_2` FOREIGN KEY (`from_section_id`) REFERENCES `warehousesections` (`section_id`) ON DELETE SET NULL,
  CONSTRAINT `stockmovements_ibfk_3` FOREIGN KEY (`to_section_id`) REFERENCES `warehousesections` (`section_id`) ON DELETE SET NULL,
  CONSTRAINT `stockmovements_chk_2` CHECK ((`quantity` > 0)),
  CONSTRAINT `stockmovements_chk_3` CHECK ((`movement_type` in (_utf8mb4'in',_utf8mb4'out',_utf8mb4'transfer',_utf8mb4'write_off'))),
  CONSTRAINT `stockmovements_chk_4` CHECK ((`movement_type` in (_utf8mb4'in',_utf8mb4'out',_utf8mb4'transfer',_utf8mb4'write_off'))),
  CONSTRAINT `stockmovements_chk_5` CHECK ((`movement_type` in (_utf8mb4'in',_utf8mb4'out',_utf8mb4'transfer',_utf8mb4'write_off')))
) ENGINE=InnoDB AUTO_INCREMENT=93 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `stockmovements`
--

LOCK TABLES `stockmovements` WRITE;
/*!40000 ALTER TABLE `stockmovements` DISABLE KEYS */;
INSERT INTO `stockmovements` VALUES (1,1,'in',3,'2026-05-16 08:52:00',NULL,5,'Надходження товару',1000.00),(2,2,'in',5,'2026-05-16 08:52:00',NULL,5,'Надходження товару',500.00),(3,3,'in',7,'2026-05-16 08:52:25',NULL,7,'Надходження товару',300.00),(4,22,'in',10,'2026-05-16 08:53:57',NULL,14,'Надходження товару',200.00),(5,17,'in',12,'2026-05-16 08:53:57',NULL,8,'Надходження товару',150.00),(6,12,'in',8,'2026-05-16 08:53:57',NULL,10,'Надходження товару',400.00),(7,13,'in',3,'2026-05-16 08:53:57',NULL,10,'Надходження товару',800.00),(8,18,'in',6,'2026-05-16 08:54:50',NULL,12,'Надходження товару',100.00),(9,20,'in',4,'2026-05-16 08:54:50',NULL,13,'Надходження товару',160.00),(10,19,'in',10,'2026-05-16 08:54:50',NULL,12,'Надходження товару',70.00),(11,21,'in',8,'2026-05-16 08:55:38',NULL,3,'Надходження товару',100.00),(12,16,'in',4,'2026-05-16 08:55:38',NULL,1,'Надходження товару',150.00),(13,15,'in',2,'2026-05-16 08:55:38',NULL,9,'Надходження товару',60.00),(14,5,'in',10,'2026-05-16 08:56:25',NULL,4,'Надходження товару',50.00),(15,6,'in',6,'2026-05-16 08:56:25',NULL,4,'Надходження товару',70.00),(16,4,'in',5,'2026-05-16 08:56:46',NULL,7,'Надходження товару',700.00),(17,14,'in',14,'2026-05-16 08:57:56',NULL,15,'Надходження товару',50.00),(18,9,'in',4,'2026-05-16 08:57:56',NULL,2,'Надходження товару',60.00),(19,11,'in',10,'2026-05-16 08:57:56',NULL,11,'Надходження товару',70.00),(20,10,'in',8,'2026-05-16 08:57:56',NULL,2,'Надходження товару',80.00),(21,7,'in',10,'2026-05-16 08:58:36',NULL,6,'Надходження товару',120.00),(22,8,'in',15,'2026-05-16 08:58:36',NULL,6,'Надходження товару',90.00),(23,22,'transfer',5,'2026-05-16 09:08:25',14,10,'Переміщення між секціями',NULL),(24,22,'transfer',5,'2026-05-16 09:08:57',10,14,'Переміщення між секціями',NULL),(25,3,'write_off',2,'2026-05-16 09:09:25',7,NULL,'Брак',NULL),(26,1,'transfer',1,'2026-05-16 09:16:28',5,19,'Збірка замовлення #1 (на перевірку)',NULL),(27,2,'transfer',1,'2026-05-16 09:16:28',5,19,'Збірка замовлення #1 (на перевірку)',NULL),(28,22,'transfer',2,'2026-05-16 09:16:28',14,19,'Збірка замовлення #1 (на перевірку)',NULL),(29,12,'transfer',2,'2026-05-16 09:16:28',10,19,'Збірка замовлення #1 (на перевірку)',NULL),(33,3,'transfer',1,'2026-05-16 09:16:34',7,19,'Збірка замовлення #2 (на перевірку)',NULL),(34,4,'transfer',1,'2026-05-16 09:16:34',7,19,'Збірка замовлення #2 (на перевірку)',NULL),(36,21,'transfer',2,'2026-05-16 09:16:40',3,19,'Збірка замовлення #3 (на перевірку)',NULL),(37,5,'transfer',8,'2026-05-16 09:16:40',4,19,'Збірка замовлення #3 (на перевірку)',NULL),(38,18,'transfer',2,'2026-05-16 09:16:40',12,19,'Збірка замовлення #3 (на перевірку)',NULL),(39,19,'transfer',5,'2026-05-16 09:16:40',12,19,'Збірка замовлення #3 (на перевірку)',NULL),(43,19,'transfer',4,'2026-05-16 09:16:46',12,19,'Збірка замовлення #4 (на перевірку)',NULL),(44,17,'transfer',5,'2026-05-16 09:16:46',8,19,'Збірка замовлення #4 (на перевірку)',NULL),(46,22,'transfer',3,'2026-05-16 09:16:52',14,19,'Збірка замовлення #5 (на перевірку)',NULL),(47,20,'transfer',2,'2026-05-16 09:16:52',13,19,'Збірка замовлення #5 (на перевірку)',NULL),(49,1,'out',1,'2026-05-16 09:19:31',5,NULL,'Масове відвантаження. Замовлення #1',NULL),(50,2,'out',1,'2026-05-16 09:19:31',5,NULL,'Масове відвантаження. Замовлення #1',NULL),(51,22,'out',2,'2026-05-16 09:19:31',14,NULL,'Масове відвантаження. Замовлення #1',NULL),(52,12,'out',2,'2026-05-16 09:19:31',10,NULL,'Масове відвантаження. Замовлення #1',NULL),(53,3,'out',1,'2026-05-16 09:19:31',7,NULL,'Масове відвантаження. Замовлення #2',NULL),(54,4,'out',1,'2026-05-16 09:19:31',7,NULL,'Масове відвантаження. Замовлення #2',NULL),(55,21,'out',2,'2026-05-16 09:19:31',3,NULL,'Масове відвантаження. Замовлення #3',NULL),(56,5,'out',8,'2026-05-16 09:19:31',4,NULL,'Масове відвантаження. Замовлення #3',NULL),(57,18,'out',2,'2026-05-16 09:19:31',12,NULL,'Масове відвантаження. Замовлення #3',NULL),(58,19,'out',5,'2026-05-16 09:19:31',12,NULL,'Масове відвантаження. Замовлення #3',NULL),(64,22,'out',3,'2026-05-16 09:19:41',14,NULL,'Масове відвантаження. Замовлення #5',NULL),(65,20,'out',2,'2026-05-16 09:19:41',13,NULL,'Масове відвантаження. Замовлення #5',NULL),(67,1,'in',150,'2026-05-16 09:23:14',NULL,5,'Надходження товару для аналітики',28000.00),(68,2,'in',200,'2026-05-16 09:23:14',NULL,5,'Надходження товару для аналітики',17500.00),(69,3,'in',80,'2026-05-16 09:23:14',NULL,7,'Надходження товару для аналітики',3200.00),(70,4,'in',60,'2026-05-16 09:23:14',NULL,7,'Надходження товару для аналітики',4500.00),(71,5,'in',500,'2026-05-16 09:23:14',NULL,4,'Надходження товару для аналітики',200.00),(72,6,'in',300,'2026-05-16 09:23:14',NULL,4,'Надходження товару для аналітики',700.00),(73,7,'in',400,'2026-05-16 09:23:14',NULL,6,'Надходження товару для аналітики',4500.00),(74,8,'in',600,'2026-05-16 09:23:14',NULL,6,'Надходження товару для аналітики',110.00),(75,9,'in',150,'2026-05-16 09:23:14',NULL,2,'Надходження товару для аналітики',280.00),(76,10,'in',250,'2026-05-16 09:23:14',NULL,2,'Надходження товару для аналітики',190.00),(77,11,'in',400,'2026-05-16 09:23:14',NULL,11,'Надходження товару для аналітики',140.00),(78,12,'in',120,'2026-05-16 09:23:14',NULL,10,'Надходження товару для аналітики',750.00),(79,13,'in',70,'2026-05-16 09:23:14',NULL,10,'Надходження товару для аналітики',2600.00),(80,14,'in',180,'2026-05-16 09:23:14',NULL,15,'Надходження товару для аналітики',600.00),(81,15,'in',350,'2026-05-16 09:23:14',NULL,9,'Надходження товару для аналітики',320.00),(82,16,'in',500,'2026-05-16 09:23:14',NULL,1,'Надходження товару для аналітики',130.00),(83,17,'in',140,'2026-05-16 09:23:14',NULL,8,'Надходження товару для аналітики',520.00),(84,18,'in',450,'2026-05-16 09:23:14',NULL,12,'Надходження товару для аналітики',270.00),(85,19,'in',90,'2026-05-16 09:23:14',NULL,12,'Надходження товару для аналітики',410.00),(86,20,'in',110,'2026-05-16 09:23:14',NULL,13,'Надходження товару для аналітики',1300.00),(87,21,'in',400,'2026-05-16 09:23:14',NULL,3,'Надходження товару для аналітики',210.00),(88,22,'in',220,'2026-05-16 09:23:14',NULL,14,'Надходження товару для аналітики',1900.00),(89,3,'transfer',3,'2026-05-16 10:22:03',7,19,'Збірка замовлення #31 (на перевірку)',NULL),(90,2,'transfer',4,'2026-05-16 10:22:03',5,19,'Збірка замовлення #31 (на перевірку)',NULL),(92,23,'in',10,'2026-05-16 10:28:30',NULL,6,'Надходження товару',100.00);
/*!40000 ALTER TABLE `stockmovements` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `suppliers`
--

DROP TABLE IF EXISTS `suppliers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `suppliers` (
  `supplier_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `type` varchar(50) NOT NULL,
  PRIMARY KEY (`supplier_id`),
  UNIQUE KEY `name` (`name`),
  CONSTRAINT `suppliers_chk_1` CHECK ((`type` in (_utf8mb4'manufacturer',_utf8mb4'distributor',_utf8mb4'wholesaler')))
) ENGINE=InnoDB AUTO_INCREMENT=2008 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `suppliers`
--

LOCK TABLES `suppliers` WRITE;
/*!40000 ALTER TABLE `suppliers` DISABLE KEYS */;
INSERT INTO `suppliers` VALUES (1,'Калениченко and Sons','distributor'),(2,'Дрозденко and Sons','wholesaler'),(3,'Данько-Приймак','manufacturer'),(4,'Артимович-Андрієвич','manufacturer'),(5,'Скопенко-Батюк','wholesaler'),(6,'Дейнека Ltd.','manufacturer'),(7,'Затула, Атаманчук and Андрусенко','wholesaler'),(8,'Гайда, Батіг and Дубенко','distributor'),(9,'Данчук-Василенко','wholesaler'),(10,'Артим, Лубенець and Бабʼюк','distributor'),(11,'Лукаш-Базилевич','wholesaler'),(12,'Шило, Яценюк and Хорішко','manufacturer'),(13,'Овчаренко-Теличенко','distributor'),(14,'Бабій Group','distributor'),(15,'Ґерета-Ґереґа','wholesaler'),(16,'Гаврюшенко, Єременко and Романчук','wholesaler'),(17,'Худяк Group','manufacturer'),(18,'Гавриленко-Макаренко','distributor'),(19,'Рудик Inc','manufacturer'),(20,'Валенко-Василашко','distributor');
/*!40000 ALTER TABLE `suppliers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `task_assignments`
--

DROP TABLE IF EXISTS `task_assignments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `task_assignments` (
  `assignment_id` int NOT NULL AUTO_INCREMENT,
  `task_id` int NOT NULL,
  `user_id` int NOT NULL,
  `assigned_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `status` enum('in_progress','done') DEFAULT 'in_progress',
  PRIMARY KEY (`assignment_id`),
  KEY `task_id` (`task_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `task_assignments_ibfk_1` FOREIGN KEY (`task_id`) REFERENCES `tasks` (`task_id`) ON DELETE CASCADE,
  CONSTRAINT `task_assignments_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=50 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `task_assignments`
--

LOCK TABLES `task_assignments` WRITE;
/*!40000 ALTER TABLE `task_assignments` DISABLE KEYS */;
INSERT INTO `task_assignments` VALUES (16,11,27,'2026-05-15 17:54:31','done'),(17,21,27,'2026-05-15 17:54:39','done'),(18,20,27,'2026-05-15 17:55:03','done'),(19,28,27,'2026-05-16 12:15:56','done'),(20,24,27,'2026-05-16 12:16:03','done'),(21,25,27,'2026-05-16 12:16:09','done'),(22,26,27,'2026-05-16 12:16:14','done'),(23,27,27,'2026-05-16 12:16:20','done'),(24,30,27,'2026-04-18 15:00:00','done'),(25,31,27,'2026-04-20 12:00:00','done'),(26,32,27,'2026-04-21 17:00:00','done'),(27,33,27,'2026-04-23 10:00:00','done'),(28,34,27,'2026-04-24 16:00:00','done'),(29,35,27,'2026-04-26 13:00:00','done'),(30,36,27,'2026-04-27 18:00:00','done'),(31,37,27,'2026-04-29 11:00:00','done'),(32,38,27,'2026-04-30 15:00:00','done'),(33,39,27,'2026-05-02 12:00:00','done'),(34,40,27,'2026-05-03 17:30:00','done'),(35,41,27,'2026-05-04 10:00:00','done'),(36,42,27,'2026-05-06 14:00:00','done'),(37,43,27,'2026-05-07 16:00:00','done'),(38,44,27,'2026-05-08 11:00:00','done'),(39,45,27,'2026-05-10 12:00:00','done'),(40,46,27,'2026-05-11 15:00:00','done'),(41,47,27,'2026-05-12 17:00:00','done'),(42,48,27,'2026-05-13 13:30:00','done'),(43,49,27,'2026-05-13 18:00:00','done'),(44,50,27,'2026-05-14 11:30:00','done'),(45,51,27,'2026-05-14 16:00:00','done'),(46,52,27,'2026-05-15 12:00:00','done'),(47,53,27,'2026-05-15 17:15:00','done'),(48,54,27,'2026-05-16 11:00:00','done'),(49,55,27,'2026-05-16 13:21:53','done');
/*!40000 ALTER TABLE `task_assignments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `task_updates`
--

DROP TABLE IF EXISTS `task_updates`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `task_updates` (
  `update_id` int NOT NULL AUTO_INCREMENT,
  `task_id` int NOT NULL,
  `updated_by` int DEFAULT NULL,
  `old_status` enum('new','in_progress','under_review','completed','cancelled') DEFAULT NULL,
  `new_status` enum('new','in_progress','under_review','completed','cancelled') DEFAULT NULL,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `comment` text,
  PRIMARY KEY (`update_id`),
  KEY `task_id` (`task_id`),
  KEY `updated_by` (`updated_by`),
  CONSTRAINT `task_updates_ibfk_1` FOREIGN KEY (`task_id`) REFERENCES `tasks` (`task_id`) ON DELETE CASCADE,
  CONSTRAINT `task_updates_ibfk_2` FOREIGN KEY (`updated_by`) REFERENCES `users` (`user_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `task_updates`
--

LOCK TABLES `task_updates` WRITE;
/*!40000 ALTER TABLE `task_updates` DISABLE KEYS */;
/*!40000 ALTER TABLE `task_updates` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tasks`
--

DROP TABLE IF EXISTS `tasks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tasks` (
  `task_id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(255) NOT NULL,
  `description` text,
  `priority` enum('low','medium','high') DEFAULT 'medium',
  `status` enum('new','in_progress','under_review','completed','cancelled') DEFAULT 'new',
  `created_by` int DEFAULT NULL,
  `deadline` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `max_assignees` int DEFAULT '1',
  `order_id` int DEFAULT NULL,
  `task_type` enum('pack','restock','other') NOT NULL DEFAULT 'other',
  PRIMARY KEY (`task_id`),
  KEY `created_by` (`created_by`),
  KEY `order_id` (`order_id`),
  CONSTRAINT `tasks_ibfk_1` FOREIGN KEY (`created_by`) REFERENCES `users` (`user_id`) ON DELETE SET NULL,
  CONSTRAINT `tasks_ibfk_2` FOREIGN KEY (`order_id`) REFERENCES `orders` (`order_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=57 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tasks`
--

LOCK TABLES `tasks` WRITE;
/*!40000 ALTER TABLE `tasks` DISABLE KEYS */;
INSERT INTO `tasks` VALUES (1,'Створити опис бананів','Напишіть по нормальному хтось опис до бананів з еквадору','high','completed',7,'2025-08-07 00:00:00','2025-08-06 13:21:13',1,NULL,'pack'),(2,'rdtfyguhijolk;l','uvhbikjnlkm;l,hbjnkm','low','cancelled',7,'2025-08-07 00:00:00','2025-08-07 14:05:09',1,NULL,'pack'),(5,'pisedrtf','sdrftgyhujxddfhgsthyts','low','under_review',7,'2025-08-10 00:00:00','2025-08-10 08:43:06',1,NULL,'pack'),(6,'sedrftygh','seeeeeeeeee','low','in_progress',7,'2025-08-10 00:00:00','2025-08-10 08:43:20',1,NULL,'pack'),(7,'llllllllll','dddddddd','low','new',7,'2025-08-10 00:00:00','2025-08-10 08:43:40',1,NULL,'pack'),(8,'ttttttt','ttttttttttt','low','new',7,'2025-08-10 00:00:00','2025-08-10 08:43:56',1,NULL,'pack'),(9,'lll','fff','low','new',7,'2025-08-10 00:00:00','2025-08-10 08:44:10',1,NULL,'pack'),(11,'Назва завдання','Опис \nпросто щось написати','low','under_review',7,'2025-11-12 00:00:00','2025-11-06 13:00:59',3,NULL,'pack'),(12,'qawer','qwasedrftg','low','new',7,'2026-02-09 00:00:00','2026-02-02 17:00:25',1,NULL,'pack'),(13,'Збірка замовлення #1633','Необхідно зібрати товари для замовлення №1633. Загальна кількість одиниць: 12.','medium','completed',7,'2026-04-17 16:31:09','2026-04-17 15:27:09',2,1633,'pack'),(14,'Збірка замовлення #1632','Необхідно зібрати товари для замовлення №1632. Загальна кількість одиниць: 100.','high','completed',7,'2026-04-18 11:26:09','2026-04-17 16:21:06',3,1632,'pack'),(15,'Збірка замовлення #1634','Необхідно зібрати товари для замовлення №1634. Загальна кількість одиниць: 1.','low','completed',7,'2026-04-18 12:03:09','2026-04-17 17:17:48',1,1634,'pack'),(16,'Збірка замовлення #1635','Необхідно зібрати товари для замовлення №1635. Загальна кількість одиниць: 2.','low','cancelled',7,'2026-04-22 15:55:46','2026-04-22 15:11:45',1,1635,'pack'),(17,'Збірка замовлення #1636','Необхідно зібрати товари для замовлення №1636. Загальна кількість одиниць: 1.','low','completed',7,'2026-04-22 16:32:46','2026-04-22 15:12:18',1,1636,'pack'),(19,'Розпакування скасованого замовлення #1635','Замовлення було скасовано на етапі collecting. Поверніть товари на полиці.','high','completed',7,NULL,'2026-04-22 17:49:21',1,1635,'restock'),(20,'Збірка замовлення #1638','Необхідно зібрати товари для замовлення №1638. Загальна кількість одиниць: 8.','low','completed',7,'2026-05-12 10:39:58','2026-05-12 09:33:57',1,1638,'pack'),(21,'Перебрати молочні продукти','щось буде','low','completed',27,'2026-05-18 17:38:54','2026-05-15 17:39:55',1,NULL,'other'),(24,'Збірка замовлення #1','Необхідно зібрати товари для замовлення №1. Загальна кількість одиниць: 6.','low','completed',7,'2026-05-23 10:04:01','2026-05-16 12:05:08',1,1,'pack'),(25,'Збірка замовлення #2','Необхідно зібрати товари для замовлення №2. Загальна кількість одиниць: 2.','low','completed',7,'2026-05-23 10:48:01','2026-05-16 12:05:44',1,2,'pack'),(26,'Збірка замовлення #3','Необхідно зібрати товари для замовлення №3. Загальна кількість одиниць: 17.','medium','completed',7,'2026-05-23 12:12:01','2026-05-16 12:06:37',2,3,'pack'),(27,'Збірка замовлення #4','Необхідно зібрати товари для замовлення №4. Загальна кількість одиниць: 9.','low','cancelled',7,'2026-05-23 13:10:01','2026-05-16 12:07:13',1,4,'pack'),(28,'Збірка замовлення #5','Необхідно зібрати товари для замовлення №5. Загальна кількість одиниць: 5.','low','completed',7,'2026-05-23 14:00:01','2026-05-16 12:07:47',1,5,'pack'),(29,'Розпакування скасованого замовлення #4','Замовлення було скасовано на етапі review_pack. Поверніть товари на полиці.','high','new',7,NULL,'2026-05-16 12:18:46',1,4,'restock'),(30,'Збірка замовлення #6','Необхідно зібрати товари для замовлення №6.','medium','completed',7,'2026-04-19 18:00:00','2026-05-16 12:34:09',1,6,'pack'),(31,'Збірка замовлення #7','Необхідно зібрати товари для замовлення №7.','medium','completed',7,'2026-04-21 18:00:00','2026-05-16 12:34:09',1,7,'pack'),(32,'Збірка замовлення #8','Необхідно зібрати товари для замовлення №8.','low','completed',7,'2026-04-22 18:00:00','2026-05-16 12:34:09',1,8,'pack'),(33,'Збірка замовлення #9','Необхідно зібрати товари для замовлення №9.','high','completed',7,'2026-04-24 18:00:00','2026-05-16 12:34:09',3,9,'pack'),(34,'Збірка замовлення #10','Необхідно зібрати товари для замовлення №10.','low','completed',7,'2026-04-25 18:00:00','2026-05-16 12:34:09',1,10,'pack'),(35,'Збірка замовлення #11','Необхідно зібрати товари для замовлення №11.','low','completed',7,'2026-04-27 18:00:00','2026-05-16 12:34:09',1,11,'pack'),(36,'Збірка замовлення #12','Необхідно зібрати товари для замовлення №12.','medium','completed',7,'2026-04-28 18:00:00','2026-05-16 12:34:09',2,12,'pack'),(37,'Збірка замовлення #13','Необхідно зібрати товари для замовлення №13.','low','completed',7,'2026-04-30 18:00:00','2026-05-16 12:34:09',1,13,'pack'),(38,'Збірка замовлення #14','Необхідно зібрати товари для замовлення №14.','low','completed',7,'2026-05-01 18:00:00','2026-05-16 12:34:09',1,14,'pack'),(39,'Збірка замовлення #15','Необхідно зібрати товари для замовлення №15.','medium','completed',7,'2026-05-03 18:00:00','2026-05-16 12:34:09',1,15,'pack'),(40,'Збірка замовлення #16','Необхідно зібрати товары для замовлення №16.','low','completed',7,'2026-05-04 18:00:00','2026-05-16 12:34:09',1,16,'pack'),(41,'Збірка замовлення #17','Необхідно зібрати товари для замовлення №17.','medium','completed',7,'2026-05-05 18:00:00','2026-05-16 12:34:09',2,17,'pack'),(42,'Збірка замовлення #18','Необхідно зібрати товари для замовлення №18.','low','completed',7,'2026-05-07 18:00:00','2026-05-16 12:34:09',1,18,'pack'),(43,'Збірка замовлення #19','Необхідно зібрати товари для замовлення №19.','high','completed',7,'2026-05-08 18:00:00','2026-05-16 12:34:09',2,19,'pack'),(44,'Збірка замовлення #20','Необхідно зібрати товари для замовлення №20.','high','completed',7,'2026-05-09 18:00:00','2026-05-16 12:34:09',3,20,'pack'),(45,'Збірка замовлення #21','Необхідно зібрати товари для замовлення №21.','low','completed',7,'2026-05-11 18:00:00','2026-05-16 12:34:09',1,21,'pack'),(46,'Збірка замовлення #22','Необхідно зібрати товари для замовлення №22.','low','completed',7,'2026-05-12 18:00:00','2026-05-16 12:34:09',1,22,'pack'),(47,'Збірка замовлення #23','Необхідно зібрати товари для замовлення №23.','high','completed',7,'2026-05-13 18:00:00','2026-05-16 12:34:09',3,23,'pack'),(48,'Збірка замовлення #24','Необхідно зібрати товари для замовлення №24.','high','completed',7,'2026-05-14 18:00:00','2026-05-16 12:34:09',3,24,'pack'),(49,'Збірка замовлення #25','Необхідно зібрати товари для замовлення №25.','low','completed',7,'2026-05-14 18:00:00','2026-05-16 12:34:09',1,25,'pack'),(50,'Збірка замовлення #26','Необхідно зібрати товари для замовлення №26.','low','completed',7,'2026-05-15 18:00:00','2026-05-16 12:34:09',1,26,'pack'),(51,'Збірка замовлення #27','Необхідно зібрати товари для замовлення №27.','high','completed',7,'2026-05-15 18:00:00','2026-05-16 12:34:09',3,27,'pack'),(52,'Збірка замовлення #28','Необхідно зібрати товари для замовлення №28.','low','completed',7,'2026-05-16 18:00:00','2026-05-16 12:34:09',1,28,'pack'),(53,'Збірка замовлення #29','Необхідно зібрати товари для замовлення №29.','high','completed',7,'2026-05-16 18:00:00','2026-05-16 12:34:09',3,29,'pack'),(54,'Збірка замовлення #30','Необхідно зібрати товари для замовлення №30.','low','completed',7,'2026-05-17 18:00:00','2026-05-16 12:34:09',1,30,'pack'),(55,'Збірка замовлення #31','Необхідно зібрати товари для замовлення №31. Загальна кількість одиниць: 7.','low','completed',7,'2026-05-16 14:14:41','2026-05-16 13:20:40',1,31,'pack'),(56,'Збірка замовлення #32','Необхідно зібрати товари для замовлення №32. Загальна кількість одиниць: 166.','high','cancelled',7,'2026-05-17 10:42:14','2026-05-16 13:30:14',3,32,'pack');
/*!40000 ALTER TABLE `tasks` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `role` enum('admin','manager','employee') NOT NULL,
  `is_temp_password` tinyint(1) DEFAULT '0',
  `employee_id` int NOT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `employee_id` (`employee_id`),
  CONSTRAINT `users_ibfk_1` FOREIGN KEY (`employee_id`) REFERENCES `employees` (`employee_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (7,'davidlevchenko','$argon2id$v=19$m=65536,t=3,p=4$XfHCAmB7IVHvK/HVoFCMPA$PMgxb9Zt086jLXqOBg9mtOqC+NLQoOtrPruo4AWH3Ac','admin',0,8),(27,'ler','$argon2id$v=19$m=65536,t=3,p=4$xSVzzPX3RuHX4vUpdjqH3g$z8MIzzL+MXPPk/HPppLnZI/5sBk1UotwqxsMHw5Hnd0','employee',0,21),(28,'admin','$argon2id$v=19$m=65536,t=3,p=4$ZwBB8GhxV9wOAAl+oBIg8w$lt3i/i4nWSqzF3LK3nURhesItI3DM9BKWwlUc5P1Q3A','admin',0,4031);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `warehousesections`
--

DROP TABLE IF EXISTS `warehousesections`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `warehousesections` (
  `section_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `location` text,
  `employee_id` int DEFAULT NULL,
  `section_type` varchar(50) NOT NULL,
  PRIMARY KEY (`section_id`),
  UNIQUE KEY `name` (`name`),
  CONSTRAINT `section_type_chk` CHECK ((`section_type` in (_utf8mb4'storage',_utf8mb4'packaging')))
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `warehousesections`
--

LOCK TABLES `warehousesections` WRITE;
/*!40000 ALTER TABLE `warehousesections` DISABLE KEYS */;
INSERT INTO `warehousesections` VALUES (1,'Секція: Автотовари','Склад А, зона 1',24,'storage'),(2,'Секція: Книги','Склад А, зона 2',26,'storage'),(3,'Секція: Побутова хімія','Склад А, зона 3',25,'storage'),(4,'Секція: Одяг','Склад А, зона 4',25,'storage'),(5,'Секція: Електроніка','Склад В, зона 1',27,'storage'),(6,'Секція: Їжа','Склад В, зона 2',26,'storage'),(7,'Секція: Меблі','Склад В, зона 3',28,'storage'),(8,'Секція: Сад та інструменти','Склад В, зона 4',27,'storage'),(9,'Секція: Здоров’я та краса','Склад С, зона 1',25,'storage'),(10,'Секція: Побутова техніка','Склад С, зона 2',23,'storage'),(11,'Секція: Канцелярія','Склад С, зона 3',29,'storage'),(12,'Секція: Зоотовари','Склад С, зона 4',29,'storage'),(13,'Секція: Спорт та туризм','Склад D, зона 1',39,'storage'),(14,'Секція: Технології','Склад D, зона 2',24,'storage'),(15,'Секція: Іграшки та ігри','Склад D, зона 3',27,'storage'),(19,'Пакувальна секція','Склад Е, зона 2',27,'packaging');
/*!40000 ALTER TABLE `warehousesections` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `prevent_multiple_packaging_sections` BEFORE INSERT ON `warehousesections` FOR EACH ROW BEGIN
    DECLARE section_count INT;
    
    SELECT COUNT(*) INTO section_count
    FROM WarehouseSections
    WHERE section_type = 'packaging';

    
    IF section_count > 0 AND NEW.section_type = 'packaging' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Only one packaging section is allowed';
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- 1. Очищення старих ролей
DROP ROLE IF EXISTS 'admin_role', 'manager_role', 'employee_role';

-- 2. Створення ролей
CREATE ROLE 'admin_role', 'manager_role', 'employee_role';

-- ==========================================
-- ПРАВА ДЛЯ EMPLOYEE (Працівник)
-- ==========================================
-- Працівник може бачити основну інформацію
GRANT SELECT ON WarehouseDB.products TO 'employee_role';
GRANT SELECT ON WarehouseDB.productcategories TO 'employee_role';
GRANT SELECT ON WarehouseDB.warehousesections TO 'employee_role';
GRANT SELECT ON WarehouseDB.employees TO 'employee_role';
GRANT SELECT ON WarehouseDB.contacts_employees TO 'employee_role';
GRANT SELECT ON WarehouseDB.suppliers TO 'employee_role';
GRANT SELECT ON WarehouseDB.customers TO 'employee_role';

-- Завдання: можна змінювати лише статус (оновлення конкретного поля)
GRANT SELECT, UPDATE (status) ON WarehouseDB.tasks TO 'employee_role';

-- Призначення завдань (task_assignments): Select, Insert, Delete 
GRANT SELECT, INSERT, DELETE ON WarehouseDB.task_assignments TO 'employee_role';
GRANT SELECT, INSERT ON WarehouseDB.task_updates TO 'employee_role';
GRANT INSERT ON WarehouseDB.stockmovements TO 'employee_role';

-- Робота з замовленнями
GRANT SELECT, UPDATE(status) ON WarehouseDB.orders TO 'employee_role';
GRANT SELECT ON WarehouseDB.orderdetails TO 'employee_role';
GRANT SELECT(user_id, employee_id) ON WarehouseDB.users TO 'employee_role';

-- ==========================================
-- ПРАВА ДЛЯ MANAGER (Менеджер)
-- ==========================================
-- Менеджер може робити майже все (ALL), крім юзерів та специфіки завдань
GRANT ALL PRIVILEGES ON WarehouseDB.products TO 'manager_role';
GRANT ALL PRIVILEGES ON WarehouseDB.productcategories TO 'manager_role';
GRANT ALL PRIVILEGES ON WarehouseDB.orders TO 'manager_role';
GRANT ALL PRIVILEGES ON WarehouseDB.orderdetails TO 'manager_role';
GRANT ALL PRIVILEGES ON WarehouseDB.customers TO 'manager_role';
GRANT ALL PRIVILEGES ON WarehouseDB.suppliers TO 'manager_role';
GRANT ALL PRIVILEGES ON WarehouseDB.contacts_customers TO 'manager_role';
GRANT ALL PRIVILEGES ON WarehouseDB.contacts_suppliers TO 'manager_role';
GRANT SELECT ON WarehouseDB.employees TO 'manager_role';
GRANT SELECT ON WarehouseDB.contacts_employees TO 'manager_role';
GRANT ALL PRIVILEGES ON WarehouseDB.stockmovements TO 'manager_role';
GRANT ALL PRIVILEGES ON WarehouseDB.reports TO 'manager_role';
GRANT ALL PRIVILEGES ON WarehouseDB.warehousesections TO 'manager_role';
GRANT ALL PRIVILEGES ON WarehouseDB.orderstatushistory TO 'manager_role';

-- Обмеження менеджера по завданнях: тільки перегляд призначень і створення
GRANT SELECT ON WarehouseDB.task_assignments TO 'manager_role';
GRANT ALL PRIVILEGES ON WarehouseDB.tasks TO 'manager_role';
GRANT SELECT(user_id, employee_id) ON WarehouseDB.users TO 'manager_role';

-- Менеджер НЕ отримує прав на таблицю Users (це для безпеки)
-- ==========================================
-- ПРАВА ДЛЯ ADMIN (Адмін)
-- ==========================================
GRANT ALL PRIVILEGES ON WarehouseDB.* TO 'admin_role' WITH GRANT OPTION;

FLUSH PRIVILEGES;

-- 1. СТВОРЕННЯ ГОЛОВНОГО АДМІНІСТРАТОРА (замінили localhost на %)
DROP USER IF EXISTS 'warehouse_admin_db'@'%';
CREATE USER 'warehouse_admin_db'@'%' IDENTIFIED BY 'Password';

GRANT ALL PRIVILEGES ON WarehouseDB.* TO 'warehouse_admin_db'@'%' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON *.* TO 'warehouse_admin_db'@'%' WITH GRANT OPTION;

-- 2. СТВОРЕННЯ ТЕХНІЧНИХ КОРИСТУВАЧІВ (замінили localhost на %)
DROP USER IF EXISTS 'auth_reader'@'%';
CREATE USER 'auth_reader'@'%' IDENTIFIED BY 'Password123';
GRANT SELECT ON WarehouseDB.users TO 'auth_reader'@'%';
GRANT SELECT ON WarehouseDB.employees TO 'auth_reader'@'%';
GRANT SELECT ON WarehouseDB.contacts_employees TO 'auth_reader'@'%';

DROP USER IF EXISTS 'password_reset_user'@'%';
CREATE USER 'password_reset_user'@'%' IDENTIFIED BY 'Password1234';
GRANT SELECT ON WarehouseDB.contacts_employees TO 'password_reset_user'@'%';
GRANT SELECT, UPDATE (password_hash, is_temp_password) ON WarehouseDB.users TO 'password_reset_user'@'%';

DROP USER IF EXISTS 'admin'@'%';
CREATE USER 'admin'@'%' IDENTIFIED BY '$argon2id$v=19$m=65536,t=3,p=4$ZwBB8GhxV9wOAAl+oBIg8w$lt3i/i4nWSqzF3LK3nURhesItI3DM9BKWwlUc5P1Q3A';
GRANT 'admin_role' TO 'admin'@'%';
SET DEFAULT ROLE 'admin_role' TO 'admin'@'%';

-- 3. ФІНАЛІЗАЦІЯ
FLUSH PRIVILEGES;