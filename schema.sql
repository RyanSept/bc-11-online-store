-- phpMyAdmin SQL Dump
-- version 4.4.15.5
-- http://www.phpmyadmin.net
--
-- Host: localhost:3306
-- Generation Time: Nov 08, 2016 at 08:01 AM
-- Server version: 5.5.49-log
-- PHP Version: 7.0.6


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `agora`
--

-- --------------------------------------------------------

--
-- Table structure for table `products`
--

CREATE TABLE IF NOT EXISTS `products` (
  `product_id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
  `product_title` varchar(255) NOT NULL,
  `product_desc` text NOT NULL,
  `product_price` float NOT NULL,
  `product_image` varchar(255) NOT NULL,
  `creation_date` date NOT NULL
) ;

-- --------------------------------------------------------

--
-- Table structure for table `shop`
--

CREATE TABLE IF NOT EXISTS `shop` (
  `shop_id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
  `shop_name` varchar(255) NOT NULL,
  `shop_desc` text NOT NULL,
  `shop_location` varchar(255) NOT NULL,
  `shop_url` varchar(255) NOT NULL
) ;

-- --------------------------------------------------------

--
-- Table structure for table `shop_products`
--

CREATE TABLE IF NOT EXISTS `shop_products` (
  `shop_id` integer NOT NULL,
  `product_id` integer NOT NULL
) ;

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE IF NOT EXISTS `users` (
  `user_id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
  `user_name` varchar(255) NOT NULL,
  `user_password` varchar(255) NOT NULL,
  `user_email` varchar(255) NOT NULL
) ;

-- --------------------------------------------------------

--
-- Table structure for table `users_shop`
--

CREATE TABLE IF NOT EXISTS `users_shop` (
  `user_id` integer NOT NULL,
  `shop_id` integer NOT NULL
) ;

--
-- Indexes for dumped tables
--

--
--

--
-- AUTO_INCREMENT for table `products`

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION ENGINE=InnoDB DEFAULT CHARSET=latin1*/;
