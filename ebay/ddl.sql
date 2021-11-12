-- auto-generated definition
create table ebay_product_info
(
    id           bigint unsigned auto_increment comment '代理主键'
        primary key,
    batch        varchar(20) charset utf8mb4  default ''                not null,
    sku_id       varchar(100) charset utf8mb4 default ''                not null,
    sku_name     varchar(100) charset utf8mb4 default ''                not null,
    price        varchar(100) charset utf8mb4 default ''                not null,
    properties   text charset utf8mb4                                   not null,
    is_delete    tinyint(1)                   default 0                 not null comment '删除标记 0:正常 1:删除',
    created_by   varchar(64) charset utf8mb4  default 'sys'             null comment '创建者',
    created_time timestamp                    default CURRENT_TIMESTAMP not null comment '创建时间',
    updated_by   varchar(64) charset utf8mb4  default 'sys'             null comment '更新者',
    updated_time timestamp                    default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP comment '更新时间'
);



-- auto-generated definition
create table ebay_table_info
(
    id           bigint unsigned auto_increment comment '代理主键'
        primary key,
    batch        varchar(20) charset utf8mb4  default ''                not null,
    sku_id       varchar(100) charset utf8mb4 default ''                not null,
    sku_name     varchar(100) charset utf8mb4 default ''                not null,
    json_text    text charset utf8mb4                                   null,
    is_delete    tinyint(1)                   default 0                 not null comment '删除标记 0:正常 1:删除',
    created_by   varchar(64) charset utf8mb4  default 'sys'             null comment '创建者',
    created_time timestamp                    default CURRENT_TIMESTAMP not null comment '创建时间',
    updated_by   varchar(64) charset utf8mb4  default 'sys'             null comment '更新者',
    updated_time timestamp                    default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP comment '更新时间'
);

