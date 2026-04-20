# project/urls.py
from django.urls import path, include
from adminuser.views.permission import (
    permission_list, permission_create, permission_update, permission_delete
)
from adminuser.views.page import (
    admin_signup, custom_admin_login, logout, AdminPasswordResetConfirmView,
    PasswordResetDone, AdminPasswordResetView, PasswordResetFinalized,
    dashboard, service_status, createAdminRoles, ListAdminRoles, role_edit,
    ListAdminUser, AdminUserDetails, AdminUserEdit, createAdminUser
)
from adminuser.views.category import (
    category_template_download, categoryAdd, categoryList, categoryDetails,
    categoryEdit, categoryStatus, categoryDelete, category_select2_list,
    categoryImport, category_export
)
from adminuser.views.brand import (
    brandList, brandAdd, brandImport, brandExport, brandTemplateDownload,
    brandDetails, brandEdit, brandDelete
)
from adminuser.views.customer import (
    CustomerDetails, CustomerCreate, CustomerList, CustomerUpdate,
    CustomerSendResetPasswordMail
)
from adminuser.views.zone import (
    ExportZone, ExportPostcode, ExportProductZonesRates, zone_rates_import,
    postcode_import, zones_import, delivery_zone_list_view, delivery_zone_create_view,
    delivery_zone_update_view, delivery_zone_delete_view, postcode_zone_list_view,
    postcode_zone_create_view, postcode_zone_update_view, delete_postcode_zone,
    shipping_rate_by_zone_list_view, shipping_rate_by_zone_create_view,
    shipping_rate_by_zone_update_view, delete_shipping_rate_by_zone,
    WarehouseListFormView, AddRateByZone, ListRateByZone, DetailRateByZone
)
from adminuser.views.email import (
    email_template_list, email_template_create, email_template_update
)
from adminuser.views.order import (
    OrderListView, OrderExportView, OrderReportPageView, order_details,
    UpdateOrderStatusView, refund_order, process_refund_action,
    process_add_timeline_entry, OrderNumberConfigView
)
from adminuser.view.vendor import (
    VendorAdd, VendorList, VendorDetails, VendorUpdate
)
from adminuser.apis.vendor_request import VendorRequestCreateAPIView
from adminuser.views.currency import (
    currencyDetail, currencyAddOrUpdate
)
from django.contrib.auth import views as auth_views
from .decorators import admin_logged_in

from adminuser.views.promotions import (
    create_promotion, edit_promotion, list_promotions, delete_promotion,
    export_promotion_template, export_promotions, import_promotions
)
from adminuser.views.coupons import (
    list_coupons, create_coupon, import_coupons, export_coupon_template,
    export_coupons, edit_coupon, delete_coupon, coupon_details,
    coupon_categories_tree, coupon_brands_list, coupon_validate_products,
    coupon_products_list
)
from adminuser.views.activity_logs import list_activity_logs
from adminuser.views.cart.coupons import (
    admin_coupon_summary_view, admin_coupon_reservations_view,
    admin_coupon_health_view, admin_user_discount_history_view,
    admin_promotion_summary_view, admin_promotion_performance_view,
    admin_discount_financial_view
)
from adminuser.views.menu import (
    menu_list, menu_create, menu_update, menu_delete, menu_items_manage,
    menu_item_delete, menu_item_update
)
from adminuser.views.email_api import send_template_email_api
from adminuser.views.return_reasons import (
    list_return_reasons, create_return_reason, edit_return_reason, delete_return_reason
)
from adminuser.views.import_export import (
    list_tasks,
    task_detail,
    order_task_details,
    task_abort,
)
from adminuser.views.return_order import (
    return_list, process_return_request, refund_process_view, process_refund_order
)
from adminuser.views.social_media import (
    social_media_list, social_media_create, social_media_update, social_media_delete
)
from adminuser.views.homepage import (
    homepage_section_list, homepage_section_add, homepage_section_edit,
    homepage_section_delete
)
from adminuser.views.faq import (
    faq_list, faq_create, faq_update, faq_delete
)
from adminuser.modules.products.views import (
    ProductBestSellerView, ProductClearanceView, ProductHotDealsView,
    ProductNewReleasesView, ProductPopularView, ProductTodaysDealView,
    ProductWhatsOnSaleView, ProductTrendingDealsView, ProductTopRatedView,
    import_reviews_view, export_reviews_view, download_reviews_template_view,
    reviews_list_view, reviews_product_list_view, review_delete_view, InventoryView
)

product_highlight = [
    # PRODUCT HIGHLIGHTS
    path(
        "product-highlights/bestseller/",
        admin_logged_in(ProductBestSellerView.as_view()),
        name="bestseller_list",
    ),
    path(
        "product-highlights/clearance/",
        admin_logged_in(ProductClearanceView.as_view()),
        name="clearance_list",
    ),
    path(
        "product-highlights/hot-deals/",
        admin_logged_in(ProductHotDealsView.as_view()),
        name="hot_deals_list",
    ),
    path(
        "product-highlights/new-releases/",
        admin_logged_in(ProductNewReleasesView.as_view()),
        name="new_releases_list",
    ),
    path(
        "product-highlights/popular/",
        admin_logged_in(ProductPopularView.as_view()),
        name="popular_list",
    ),
    path(
        "product-highlights/todays-deals/",
        admin_logged_in(ProductTodaysDealView.as_view()),
        name="todays_deals_list",
    ),
    path(
        "product-highlights/whats-on-sale/",
        admin_logged_in(ProductWhatsOnSaleView.as_view()),
        name="whats_on_sale_list",
    ),
    path(
        "product-highlights/trending-deals/",
        admin_logged_in(ProductTrendingDealsView.as_view()),
        name="trending_deals_list",
    ),
    path(
        "product-highlights/top-rated/",
        admin_logged_in(ProductTopRatedView.as_view()),
        name="top_rated_list",
    ),
]
category_urls = [
    path(
        "category/template/download",
        admin_logged_in(category_template_download),
        name="category_template_download",
    ),
    path("category/add", admin_logged_in(categoryAdd), name="category_add"),
    path("category/list", admin_logged_in(categoryList), name="category_list"),
    path(
        "category/<str:id>", admin_logged_in(categoryDetails), name="category_details"
    ),
    path("category/edit/<str:id>", admin_logged_in(categoryEdit), name="category_edit"),
    path(
        "category/status/<str:id>",
        admin_logged_in(categoryStatus),
        name="category_status",
    ),
    path(
        "category/delete/<str:id>",
        admin_logged_in(categoryDelete),
        name="category_delete",
    ),
    path(
        "category/api/select2",
        admin_logged_in(category_select2_list),
        name="category_select2_api",
    ),
]
brand_urls = [
    # Brand
    path("brand/list", admin_logged_in(brandList), name="brand_list"),
    path("brand/add", admin_logged_in(brandAdd), name="brand_add"),
    path("brand/import", admin_logged_in(brandImport), name="brand_import"),
    path("brand/export", admin_logged_in(brandExport), name="brand_export"),
    path(
        "brand/template/download",
        admin_logged_in(brandTemplateDownload),
        name="brand_template_download",
    ),
    path("brand/<str:id>", admin_logged_in(brandDetails), name="brand_details"),
    path("brand/edit/<str:id>", admin_logged_in(brandEdit), name="brand_edit"),
    path("brand/delete/<str:id>", admin_logged_in(brandDelete), name="brand_delete"),
]
customer_urls = [
    path(
        "customer/<str:id>/details",
        admin_logged_in(CustomerDetails),
        name="user_detail",
    ),
    path(
        "customer/create",
        admin_logged_in(CustomerCreate),
        name="customer_create",
    ),
    path(
        "customer/list",
        admin_logged_in(CustomerList),
        name="customer_list",
    ),
    path(
        "customer/<str:id>/update",
        admin_logged_in(CustomerUpdate),
        name="customer_update",
    ),
    path(
        "customer/<str:id>/reset_password",
        admin_logged_in(CustomerSendResetPasswordMail),
        name="customer_reset_password",
    ),
]
coupons_urls = [
    path("coupons/", admin_logged_in(list_coupons), name="coupon_list_form"),
    path("coupons/create/", admin_logged_in(create_coupon), name="coupon_create"),
    path(
        "coupons/import-template",
        admin_logged_in(import_coupons),
        name="coupon_import_template",
    ),
    path(
        "coupons/export-template",
        admin_logged_in(export_coupon_template),
        name="export_coupon_template",
    ),
    path("coupons/export/", admin_logged_in(export_coupons), name="export_coupons"),
    path(
        "coupons/update/<str:id>/", admin_logged_in(edit_coupon), name="coupon_update"
    ),
    path(
        "coupons/<str:id>/delete", admin_logged_in(delete_coupon), name="coupon_delete"
    ),
    path("coupons/<str:id>/", admin_logged_in(coupon_details), name="coupon_details"),
    # Item-selector AJAX APIs
    path(
        "coupons/api/categories-tree",
        admin_logged_in(coupon_categories_tree),
        name="coupon_categories_tree",
    ),
    path(
        "coupons/api/brands",
        admin_logged_in(coupon_brands_list),
        name="coupon_brands_list",
    ),
    path(
        "coupons/api/validate-products",
        admin_logged_in(coupon_validate_products),
        name="coupon_validate_products",
    ),
    path(
        "coupons/api/products",
        admin_logged_in(coupon_products_list),
        name="coupon_products_list",
    ),
]
return_reasons_urls = [
    path("return-reasons/", list_return_reasons, name="return_reason_list"),
    path("return-reasons/create/", create_return_reason, name="create_return_reason"),
    path(
        "return-reasons/edit/<str:reason_id>/",
        edit_return_reason,
        name="edit_return_reason",
    ),
    path(
        "return-reasons/delete/<str:reason_id>/",
        delete_return_reason,
        name="delete_return_reason",
    ),
]
order_urls = [
    path(
        "orders/rate_by_zone",
        admin_logged_in(AddRateByZone),
        name="rate_by_zone_add",
    ),
    path(
        "orders/rate_by_zone/list",
        admin_logged_in(ListRateByZone),
        name="rate_by_zone_list",
    ),
    path(
        "orders/rate_by_zone/<str:id>/detail",
        admin_logged_in(DetailRateByZone),
        name="rate_by_zone_detail",
    ),
    path(
        "orders/list",
        admin_logged_in(OrderListView.as_view()),
        name="order_list",
    ),
    path(
        "orders/export",
        admin_logged_in(OrderExportView.as_view()),
        name="export_orders",
    ),
    path(
        "orders/report",
        admin_logged_in(OrderReportPageView.as_view()),
        name="order_report_page",
    ),
    path(
        "orders/<str:order_id>/details",
        admin_logged_in(order_details),
        name="order_details",
    ),
    path(
        "orders/<str:order_id>/update-status",
        admin_logged_in(UpdateOrderStatusView.as_view()),
        name="order_update_status",
    ),
    path(
        "orders/<str:order_id>/refund",
        admin_logged_in(refund_order),
        name="order_refund",
    ),
    path(
        "orders/<str:order_id>/refund-api",
        admin_logged_in(process_refund_action),
        name="process_order_refund_api",
    ),
    path(
        "orders/<str:order_id>/timeline",
        admin_logged_in(process_add_timeline_entry),
        name="add_order_timeline_entry",
    ),
    path(
        "orders/order-number-config",
        admin_logged_in(OrderNumberConfigView.as_view()),
        name="order_number_config",
    ),
]
returns = [
    path("returns/list", admin_logged_in(return_list), name="return_list"),
    path(
        "returns/process/<str:return_id>",
        admin_logged_in(process_return_request),
        name="process_return_request",
    ),
    path(
        "returns/refund/<str:return_id>",
        admin_logged_in(refund_process_view),
        name="refund_process_view",
    ),
    path(
        "returns/api/refund-order/<str:order_id>",
        admin_logged_in(process_refund_order),
        name="process_refund_order",
    ),
]
homepage_urls = [
    path(
        "homepage/sections/list",
        admin_logged_in(homepage_section_list),
        name="homepage_section_list",
    ),
    path(
        "homepage/sections/add",
        admin_logged_in(homepage_section_add),
        name="homepage_section_add",
    ),
    path(
        "homepage/sections/edit/<str:section_type>",
        admin_logged_in(homepage_section_edit),
        name="homepage_section_edit",
    ),
    path(
        "homepage/sections/delete/<str:section_type>",
        admin_logged_in(homepage_section_delete),
        name="homepage_section_delete",
    ),
]
auth_urls = [
    path("signup/", admin_signup, name="admin-signup"),
    path("", custom_admin_login, name="admin-login"),
    path("logout", logout, name="logout"),
    path(
        "reset/<uidb64>/<token>/",
        AdminPasswordResetConfirmView.as_view(),
        name="admin_password_reset_confirm",
    ),
    path("password-reset/done/", PasswordResetDone),
    path(
        "password-reset/", AdminPasswordResetView.as_view(), name="admin_password_reset"
    ),
    path("reset/done", PasswordResetFinalized),
]
urlpatterns = [
    # ACCOUNT
    path("dashboard", admin_logged_in(dashboard), name="admin_dashboard"),
    # END ACCOUNT
    # ADMIN USER
    path("service/status", admin_logged_in(service_status), name="service_status_list"),
    path(
        "create-admin-role", admin_logged_in(createAdminRoles), name="adminrole_create"
    ),
    path("list-admin-role", admin_logged_in(ListAdminRoles), name="adminrole_list"),
    path(
        "admin-role/<int:id>/edit",
        admin_logged_in(role_edit),
        name="adminrole_edit",
    ),
    path("permissions/list", admin_logged_in(permission_list), name="permission_list"),
    path(
        "permissions/create",
        admin_logged_in(permission_create),
        name="permission_create",
    ),
    path(
        "permissions/update/<int:pk>",
        admin_logged_in(permission_update),
        name="permission_update",
    ),
    path(
        "permissions/delete/<int:pk>",
        admin_logged_in(permission_delete),
        name="permission_delete",
    ),
    path("list-admin-users", admin_logged_in(ListAdminUser), name="adminuser_list"),
    path(
        "Admin-user/<int:id>",
        admin_logged_in(AdminUserDetails),
        name="adminuser_details",
    ),
    path(
        "Admin-user/<int:id>/edit",
        admin_logged_in(AdminUserEdit),
        name="adminuser_edit",
    ),
    path("create-admin", admin_logged_in(createAdminUser), name="adminuser_create"),
    # PRODUCT - CATEGORY
    path("category/import", admin_logged_in(categoryImport), name="category_import"),
    path("category/export", admin_logged_in(category_export), name="category_export"),
    path("product", include("adminuser.modules.products.urls")),
    # path(
    #     "product/template/price_qty/download",
    #     admin_logged_in(product_price_qty_template_download_view),
    #     name="product_price_qty_template_download",
    # ),
    # path(
    #     "product/price_qty/upload",
    #     admin_logged_in(price_qty_import),
    #     name="price_qty_import",
    # ),
    path("currency", admin_logged_in(currencyDetail), name="currency"),
    path(
        "currency/update",
        admin_logged_in(currencyAddOrUpdate),
        name="currency_add_or_update",
    ),
    # Customer User
    path(
        "vendor/add",
        admin_logged_in(VendorAdd),
        name="vendor_add",
    ),
    path(
        "vendor/list",
        admin_logged_in(VendorList),
        name="vendor_list",
    ),
    path(
        "vendor/<int:id>",
        admin_logged_in(VendorDetails),
        name="vendor_details",
    ),
    path(
        "vendor/<int:id>/edit",
        admin_logged_in(VendorUpdate),
        name="vendor_update",
    ),
    path(
        "api/vendor/request",
        VendorRequestCreateAPIView.as_view(),
        name="api_vendor_request_create",
    ),
    # ZONES
    path(
        "zone/export",
        admin_logged_in(ExportZone),
        name="zone_export",
    ),
    path(
        "postcode/export",
        admin_logged_in(ExportPostcode),
        name="postcode_export",
    ),
    path(
        "product-zones-rates/export",
        admin_logged_in(ExportProductZonesRates),
        name="product_zones_rates_export",
    ),
    path(
        "product-zones-rates/import",
        admin_logged_in(zone_rates_import),
        name="product_zones_rates_import",
    ),
    path(
        "postcode/import",
        admin_logged_in(postcode_import),
        name="postcode_import",
    ),
    path(
        "order/task/details/<str:id>",
        admin_logged_in(order_task_details),
        name="order_task_details",
    ),
    path(
        "zones/import",
        admin_logged_in(zones_import),
        name="zones_import",
    ),
    path(
        "zones",
        admin_logged_in(delivery_zone_list_view),
        name="delivery_zone_list_form",
    ),
    path(
        "zones/create",
        admin_logged_in(delivery_zone_create_view),
        name="delivery_zone_create",
    ),
    path(
        "zones/update/<str:id>",
        admin_logged_in(delivery_zone_update_view),
        name="delivery_zone_update",
    ),
    path(
        "zones/delete/<str:id>",
        admin_logged_in(delivery_zone_delete_view),
        name="delivery_zone_delete",
    ),
    path(
        "postcode-zones/",
        admin_logged_in(postcode_zone_list_view),
        name="postcode_zone_list_form",
    ),
    path(
        "postcode-zones/create/",
        admin_logged_in(postcode_zone_create_view),
        name="postcode_zone_create",
    ),
    path(
        "postcode-zones/update/<str:id>/",
        admin_logged_in(postcode_zone_update_view),
        name="postcode_zone_update",
    ),
    path(
        "postcode-zones/delete/<str:id>/",
        admin_logged_in(delete_postcode_zone),
        name="postcode_zone_delete",
    ),
    # shipping rate by zone
    path(
        "shipping-rate-zones/",
        admin_logged_in(shipping_rate_by_zone_list_view),
        name="shipping_rate_by_zone_list_form",
    ),
    path(
        "shipping-rate-zones/create/",
        admin_logged_in(shipping_rate_by_zone_create_view),
        name="shipping_rate_by_zone_create",
    ),
    path(
        "shipping-rate-zones/update/<str:id>/",
        admin_logged_in(shipping_rate_by_zone_update_view),
        name="shipping_rate_by_zone_update",
    ),
    path(
        "shipping-rate-zones/delete/<str:id>/",
        admin_logged_in(delete_shipping_rate_by_zone),
        name="shipping_rate_by_zone_delete",
    ),
    path(
        "import-export/list-tasks",
        admin_logged_in(list_tasks),
        name="import_export_list_tasks",
    ),
    path(
        "import-export/task-detail/<str:id>",
        admin_logged_in(task_detail),
        name="task_detail",
    ),
    path(
        "import-export/task-detail/<str:id>/abort",
        admin_logged_in(task_abort),
        name="task_abort",
    ),
    # ADMIN ANALYTICS ROUTES
    path(
        "monitor/coupon-summary",
        admin_logged_in(admin_coupon_summary_view),
        name="admin_coupon_summary",
    ),
    path(
        "monitor/promotion-summary",
        admin_logged_in(admin_promotion_summary_view),
        name="admin_promotion_summary",
    ),
    path(
        "monitor/discount-financial",
        admin_logged_in(admin_discount_financial_view),
        name="admin_discount_financial_summary",
    ),
    path(
        "monitor/coupon-reservations",
        admin_logged_in(admin_coupon_reservations_view),
        name="admin_coupon_reservations",
    ),
    path(
        "monitor/coupon-health",
        admin_logged_in(admin_coupon_health_view),
        name="admin_coupon_health",
    ),
    path(
        "monitor/user-discount-history",
        admin_logged_in(admin_user_discount_history_view),
        name="admin_user_discount_history",
    ),
    path(
        "monitor/promotion-performance/<str:promotion_id>",
        admin_logged_in(admin_promotion_performance_view),
        name="admin_promotion_performance",
    ),
    path(
        "warehouses/",
        admin_logged_in(WarehouseListFormView.as_view()),
        name="warehouse_list_form",
    ),
    # EMAIL MODULE
    path("email/", include("adminuser.modules.email.urls")),
    # OLD EMAIL VIEWS (Keeping for compatibility or reference if needed)
    path(
        "templates/",
        admin_logged_in(email_template_list),
        name="email_template_list_old",
    ),
    path(
        "templates/create/",
        admin_logged_in(email_template_create),
        name="email_template_create_old",
    ),
    path(
        "templates/<int:pk>/update/",
        admin_logged_in(email_template_update),
        name="email_template_update_old",
    ),
    path(
        "api/email/send-template/", send_template_email_api, name="send_template_email"
    ),
    path(
        "create-promotions/", admin_logged_in(create_promotion), name="create_promotion"
    ),
    path(
        "edit-promotions/<str:promotion_id>/",
        admin_logged_in(edit_promotion),
        name="edit_promotion",
    ),
    path("list-promotions/", admin_logged_in(list_promotions), name="list_promotions"),
    path(
        "delete-promotions/<str:promotion_id>/",
        admin_logged_in(delete_promotion),
        name="delete_promotion",
    ),
    path(
        "promotions-export-template/",
        admin_logged_in(export_promotion_template),
        name="export_template",
    ),
    path(
        "promotions-export/",
        admin_logged_in(export_promotions),
        name="export_promotions",
    ),
    path(
        "promotions-import-template/",
        admin_logged_in(import_promotions),
        name="import_promotions",
    ),
    path("activity-logs/", admin_logged_in(list_activity_logs), name="activity_logs"),
    path(
        "reviews/import/", admin_logged_in(import_reviews_view), name="import_reviews"
    ),
    path(
        "reviews/export/", admin_logged_in(export_reviews_view), name="export_reviews"
    ),
    path(
        "reviews/template/",
        admin_logged_in(download_reviews_template_view),
        name="download_reviews_template",
    ),
    path("reviews/list/", admin_logged_in(reviews_list_view), name="reviews_list"),
    path(
        "reviews/product/<str:id>",
        admin_logged_in(reviews_product_list_view),
        name="reviews_product_list",
    ),
    path(
        "reviews/product/<str:id>/delete/<str:review_id>",
        admin_logged_in(review_delete_view),
        name="delete_review",
    ),
    path(
        "inventory/list/",
        admin_logged_in(InventoryView.as_view()),
        name="inventory_list",
    ),
    # MENU
    path("menu/list", admin_logged_in(menu_list), name="menu_list"),
    path("menu/create", admin_logged_in(menu_create), name="menu_create"),
    path("menu/<int:pk>/update", admin_logged_in(menu_update), name="menu_update"),
    path("menu/<int:pk>/delete", admin_logged_in(menu_delete), name="menu_delete"),
    path(
        "menu/<int:pk>/items",
        admin_logged_in(menu_items_manage),
        name="menu_items_manage",
    ),
    path(
        "menu/items/<int:pk>/delete",
        admin_logged_in(menu_item_delete),
        name="menu_item_delete",
    ),
    path(
        "menu/items/<int:pk>/update",
        admin_logged_in(menu_item_update),
        name="menu_item_update",
    ),
    # COURIERS
    path("couriers/", include("adminuser.modules.couriers.urls")),
    # RETURNS
    # SOCIAL MEDIA LINKS
    path(
        "social-media/list",
        admin_logged_in(social_media_list),
        name="social_media_list",
    ),
    path(
        "social-media/create",
        admin_logged_in(social_media_create),
        name="social_media_create",
    ),
    path(
        "social-media/<int:pk>/update",
        admin_logged_in(social_media_update),
        name="social_media_update",
    ),
    path(
        "social-media/<int:pk>/delete",
        admin_logged_in(social_media_delete),
        name="social_media_delete",
    ),
    # FAQ
    path("faq/list", admin_logged_in(faq_list), name="faq_list"),
    path("faq/create", admin_logged_in(faq_create), name="faq_create"),
    path("faq/edit/<int:id>", admin_logged_in(faq_update), name="faq_edit"),
    path("faq/delete/<int:id>", admin_logged_in(faq_delete), name="faq_delete"),
]

urlpatterns.extend(auth_urls)

urlpatterns.extend(product_highlight)
urlpatterns.extend(category_urls)
urlpatterns.extend(brand_urls)
urlpatterns.extend(customer_urls)
urlpatterns.extend(coupons_urls)
urlpatterns.extend(return_reasons_urls)
urlpatterns.extend(order_urls)
urlpatterns.extend(returns)
urlpatterns.extend(homepage_urls)
