-- MySQL dump 10.13  Distrib 9.0.1, for macos15.1 (arm64)
--
-- Host: localhost    Database: Tutoring_Center
-- ------------------------------------------------------
-- Server version	9.0.1

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
-- Table structure for table `DISCIPLINE`
--

DROP TABLE IF EXISTS `DISCIPLINE`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `DISCIPLINE` (
  `DisciplineID` int NOT NULL AUTO_INCREMENT,
  `DisciplineName` varchar(50) NOT NULL,
  PRIMARY KEY (`DisciplineID`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `DISCIPLINE`
--

LOCK TABLES `DISCIPLINE` WRITE;
/*!40000 ALTER TABLE `DISCIPLINE` DISABLE KEYS */;
INSERT INTO `DISCIPLINE` VALUES (1,'Biology'),(2,'Business'),(3,'Chemistry'),(4,'Computer Science'),(5,'Criminal Justice'),(6,'Info and Stats'),(7,'Mathematics'),(8,'Physics');
/*!40000 ALTER TABLE `DISCIPLINE` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `LOGIN`
--

DROP TABLE IF EXISTS `LOGIN`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `LOGIN` (
  `Email` varchar(25) NOT NULL,
  `Pword` varchar(50) NOT NULL,
  PRIMARY KEY (`Email`),
  CONSTRAINT `LOGINFK` FOREIGN KEY (`Email`) REFERENCES `USERS` (`Email`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `LOGIN`
--

LOCK TABLES `LOGIN` WRITE;
/*!40000 ALTER TABLE `LOGIN` DISABLE KEYS */;
INSERT INTO `LOGIN` VALUES ('admin@admin.com','root'),('gonza467@go.stockton.edu','admin');
/*!40000 ALTER TABLE `LOGIN` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `SCHEDULE`
--

DROP TABLE IF EXISTS `SCHEDULE`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `SCHEDULE` (
  `Email` varchar(50) NOT NULL,
  `DayOfWeek` varchar(10) NOT NULL,
  `StartTime` time NOT NULL,
  `Loc` varchar(25) DEFAULT NULL,
  `Approved` varchar(3) DEFAULT NULL,
  PRIMARY KEY (`Email`,`DayOfWeek`,`StartTime`),
  CONSTRAINT `ScheduleFK1` FOREIGN KEY (`Email`) REFERENCES `USERS` (`Email`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `SCHEDULE`
--

LOCK TABLES `SCHEDULE` WRITE;
/*!40000 ALTER TABLE `SCHEDULE` DISABLE KEYS */;
INSERT INTO `SCHEDULE` VALUES ('gonza467@go.stockton.edu','Monday','08:00:00','Online','Yes'),('gonza467@go.stockton.edu','Monday','08:30:00','J106','Yes'),('gonza467@go.stockton.edu','Monday','09:00:00','J106','Yes'),('gonza467@go.stockton.edu','Tuesday','08:30:00','Online','Yes'),('gonza467@go.stockton.edu','Tuesday','09:00:00','Online','Yes'),('gonza467@go.stockton.edu','Tuesday','09:30:00','Online','No');
/*!40000 ALTER TABLE `SCHEDULE` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `SUBJECT_GROUPS`
--

DROP TABLE IF EXISTS `SUBJECT_GROUPS`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `SUBJECT_GROUPS` (
  `DisciplineID` int NOT NULL,
  `SubjectID` int NOT NULL,
  PRIMARY KEY (`DisciplineID`,`SubjectID`),
  KEY `Subject_GroupsFK2` (`SubjectID`),
  CONSTRAINT `Subject_GroupsFK1` FOREIGN KEY (`DisciplineID`) REFERENCES `DISCIPLINE` (`DisciplineID`) ON DELETE CASCADE,
  CONSTRAINT `Subject_GroupsFK2` FOREIGN KEY (`SubjectID`) REFERENCES `SUBJECT_LIST` (`SubjectID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `SUBJECT_GROUPS`
--

LOCK TABLES `SUBJECT_GROUPS` WRITE;
/*!40000 ALTER TABLE `SUBJECT_GROUPS` DISABLE KEYS */;
INSERT INTO `SUBJECT_GROUPS` VALUES (7,1001),(1,1002),(1,1003),(1,1004),(1,1005),(2,1006),(2,1007),(2,1008),(2,1009),(2,1010),(3,1011),(3,1012),(3,1013),(3,1014),(4,1015),(4,1016),(4,1017),(5,1018),(5,1019),(5,1020),(5,1021),(6,1022),(6,1023),(6,1024),(6,1025),(6,1026),(6,1027),(7,1028),(7,1029),(7,1030),(7,1031),(7,1032),(7,1033),(7,1034),(7,1035),(7,1036),(7,1037),(7,1038),(7,1039),(7,1040),(7,1041),(8,1042),(8,1043),(8,1044),(8,1045),(8,1046),(8,1047);
/*!40000 ALTER TABLE `SUBJECT_GROUPS` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `SUBJECT_LIST`
--

DROP TABLE IF EXISTS `SUBJECT_LIST`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `SUBJECT_LIST` (
  `SubjectID` int NOT NULL AUTO_INCREMENT,
  `SubjectName` varchar(50) NOT NULL,
  PRIMARY KEY (`SubjectID`)
) ENGINE=InnoDB AUTO_INCREMENT=1048 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `SUBJECT_LIST`
--

LOCK TABLES `SUBJECT_LIST` WRITE;
/*!40000 ALTER TABLE `SUBJECT_LIST` DISABLE KEYS */;
INSERT INTO `SUBJECT_LIST` VALUES (1001,'Linear Algebra'),(1002,'Biochemistry'),(1003,'Biodiversity and Evolution'),(1004,'Cells and Molecules'),(1005,'Genetics'),(1006,'Cost Accounting'),(1007,'Financial Accounting'),(1008,'Intermediate Accounting I'),(1009,'Intro to Business Analytics'),(1010,'Managerial Accounting'),(1011,'Chemistry I'),(1012,'Chemistry II'),(1013,'Chemistry III'),(1014,'Chemistry IV'),(1015,'Computer Organization'),(1016,'Data Structures and Algorithms I'),(1017,'Foundations of Computer Science'),(1018,'Ecological Economics'),(1019,'Intermediate Macroeconomics'),(1020,'Macroeconomics'),(1021,'Microeconomics'),(1022,'Advanced Statistics'),(1023,'Experimental Psychology'),(1024,'Programming and Problem Solving I'),(1025,'Programming and Problem Solving II'),(1026,'Psych Statistics'),(1027,'Statistics'),(1028,'Algebraic Problem Solving/Intermediate Algebra'),(1029,'Calculus'),(1030,'Calculus 2'),(1031,'Calculus 3'),(1032,'Developmental Mathematics'),(1033,'Differential Equations'),(1034,'Discrete Mathematics'),(1035,'Geometry for Teachers'),(1036,'Numerical Analysis'),(1037,'Precalculus'),(1038,'Probability and Statistics I'),(1039,'Probability and Data Analysis'),(1040,'Proof Through Algebra'),(1041,'Quantitative Reasoning I'),(1042,'Physics for Life Sciences I'),(1043,'Physics for Life Sciences II'),(1044,'Physics I'),(1045,'Physics II'),(1046,'Physics III'),(1047,'Statics');
/*!40000 ALTER TABLE `SUBJECT_LIST` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `SUBJECTS`
--

DROP TABLE IF EXISTS `SUBJECTS`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `SUBJECTS` (
  `Email` varchar(50) NOT NULL,
  `SubjectID` int NOT NULL,
  PRIMARY KEY (`Email`,`SubjectID`),
  KEY `SubjectsFK2` (`SubjectID`),
  CONSTRAINT `SubjectsFK1` FOREIGN KEY (`Email`) REFERENCES `USERS` (`Email`) ON DELETE CASCADE,
  CONSTRAINT `SubjectsFK2` FOREIGN KEY (`SubjectID`) REFERENCES `SUBJECT_LIST` (`SubjectID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `SUBJECTS`
--

LOCK TABLES `SUBJECTS` WRITE;
/*!40000 ALTER TABLE `SUBJECTS` DISABLE KEYS */;
INSERT INTO `SUBJECTS` VALUES ('gonza467@go.stockton.edu',1002),('gonza467@go.stockton.edu',1012);
/*!40000 ALTER TABLE `SUBJECTS` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `USERS`
--

DROP TABLE IF EXISTS `USERS`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `USERS` (
  `Email` varchar(50) NOT NULL,
  `FirstName` varchar(25) NOT NULL,
  `LastName` varchar(25) NOT NULL,
  `Tutor` varchar(5) DEFAULT NULL,
  `Admin` varchar(5) DEFAULT NULL,
  PRIMARY KEY (`Email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `USERS`
--

LOCK TABLES `USERS` WRITE;
/*!40000 ALTER TABLE `USERS` DISABLE KEYS */;
INSERT INTO `USERS` VALUES ('admin@admin.com','Admin','Admin','No','Yes'),('gonza467@go.stockton.edu','Alexis','Gonzalez','Yes','Yes');
/*!40000 ALTER TABLE `USERS` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-11-24 13:26:55
