ALTER TABLE `ecofunds`.`ecofunds_entity_locations` ADD COLUMN `id` BIGINT(20) NOT NULL AUTO_INCREMENT  AFTER `entity_id` 
, ADD UNIQUE KEY (`id`) ;

ALTER TABLE `ecofunds`.`ecofunds_entity_attachments` ADD COLUMN `id` BIGINT(20) NOT NULL AUTO_INCREMENT  AFTER `entity_id` 
, ADD UNIQUE KEY (`id`) ;

ALTER TABLE `ecofunds`.`ecofunds_organization_attachments` ADD COLUMN `id` BIGINT(20) NOT NULL AUTO_INCREMENT  AFTER `organization_id` 
, ADD UNIQUE KEY (`id`) ;

ALTER TABLE `ecofunds`.`ecofunds_investment_attachments` ADD COLUMN `id` BIGINT(20) NOT NULL AUTO_INCREMENT  AFTER `investment_id` 
, ADD UNIQUE KEY (`id`) ;
