-- CreateTable
CREATE TABLE `user` (
    `id` BIGINT NOT NULL AUTO_INCREMENT,
    `username` VARCHAR(191) NOT NULL,

    UNIQUE INDEX `user_username_key`(`username`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `bot` (
    `id` BIGINT NOT NULL AUTO_INCREMENT,
    `user_id` BIGINT NOT NULL,
    `fast_engine` VARCHAR(191) NOT NULL,
    `smart_engine` VARCHAR(191) NOT NULL,
    `image_size` INTEGER NOT NULL,
    `fast_tokens` INTEGER NOT NULL,
    `smart_tokens` INTEGER NOT NULL,
    `ai_settings` JSON NOT NULL,
    `worker_message_id` VARCHAR(191) NULL,
    `runs_left` INTEGER NOT NULL DEFAULT 0,
    `created_dt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updated_dt` DATETIME(3) NOT NULL,
    `is_active` BOOLEAN NOT NULL DEFAULT true,
    `is_failed` BOOLEAN NOT NULL DEFAULT false,

    UNIQUE INDEX `bot_user_id_key`(`user_id`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- AddForeignKey
ALTER TABLE `bot` ADD CONSTRAINT `bot_user_id_fkey` FOREIGN KEY (`user_id`) REFERENCES `user`(`id`) ON DELETE CASCADE ON UPDATE CASCADE;
