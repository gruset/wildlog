// WildLog i18n — translation dictionary
// Usage: t('key') returns the string in the current language

const LANGS = {
  en: {
    // ── Nav ───────────────────────────────────────────────
    nav_dashboard:     '📊 Dashboard',
    nav_top_list:      '🏆 Top List',
    nav_log:           '📋 Game Log',
    nav_add_entry:     '➕ Add Entry',
    nav_hunters:       '👤 Hunters',
    nav_saved_views:   '🔖 Saved Views',
    nav_embeds:        '📡 Embeds',
    nav_users:         '👥 Users',
    nav_associations:  '🏕 Associations',

    // ── Header / user menu ───────────────────────────────
    assoc_label:       'Association',
    all_associations:  'All associations',
    change_password:   '🔑 Change Password',
    sign_out:          '↪ Sign Out',
    language:          '🌐 Language',

    // ── Dashboard ────────────────────────────────────────
    stat_total:        'Total Game',
    stat_hunters:      'Hunters',
    stat_species:      'Species',
    stat_best:         'Top Hunter',
    chart_per_hunter:  'Game per Hunter — Overview',
    chart_by_species:  'By Species',
    recent_entries:    'Recent Entries',

    // ── Leaderboard ──────────────────────────────────────
    filter_leaderboard: '⚙ Filter Leaderboard',
    lbl_hunters:       'Hunters',
    lbl_species:       'Species',
    lbl_location:      'Location',
    lbl_year_from:     'Year From',
    lbl_year_to:       'Year To',
    lbl_group_by:      'Group By',
    group_hunter:      'Hunter',
    group_species:     'Species',
    btn_apply:         'Apply Filters',
    btn_reset:         'Reset',
    btn_save_view:     '🔖 Save This View',
    leaderboard_chart: 'Leaderboard Chart',

    // ── Log ──────────────────────────────────────────────
    filter_log:        '⚙ Filter Log',
    lbl_hunter:        'Hunter',
    lbl_search:        'Search',
    btn_filter:        'Filter',
    btn_clear:         'Clear',
    all_entries:       'All Entries',
    col_hunter:        'Hunter',
    col_species:       'Species',
    col_count:         'Count',
    col_date:          'Date',
    col_location:      'Location',
    col_notes:         'Notes',

    // ── Add Entry ────────────────────────────────────────
    add_entry_title:   'Add Game Entry',
    lbl_hunter_req:    'Hunter *',
    lbl_species_req:   'Species *',
    lbl_count_req:     'Count *',
    lbl_date_req:      'Hunt Date *',
    lbl_location:      'Location',
    lbl_notes:         'Notes',
    btn_save_entry:    'Save Entry',
    btn_clear_form:    'Clear',
    assoc_context:     'Association context',
    assoc_hint_admin:  'Filter the hunter dropdown by association.',
    assoc_hint_aa:     'Select the association to add entries for.',
    logging_as:        'Logging as',
    no_hunter_linked:  'Your account is not linked to a hunter — contact an admin.',
    adding_for_assoc:  'Adding entry for your association hunters.',

    // ── Hunters ──────────────────────────────────────────
    add_hunter_title:  'Add Hunter',
    lbl_name_req:      'Name *',
    lbl_associations:  'Associations',
    btn_add_hunter:    'Add Hunter',
    all_hunters_title: 'All Hunters',
    col_name:          'Name',
    col_total_game:    'Total Game',
    col_member_since:  'Member Since',
    col_assocs:        'Associations',
    no_hunters:        'No hunters yet.',

    // ── Saved Views ──────────────────────────────────────
    saved_views_title: 'Saved Views',
    saved_views_hint:  'Create a view on the Leaderboard page by setting filters and clicking "Save This View".',
    my_views:          'My Views',
    shared_views:      'Shared Views',
    shared_views_sub:  '— click to apply, editing not available',
    no_views:          'No saved views yet.',

    // ── Embeds ───────────────────────────────────────────
    create_embed_title: 'Create Embed',
    create_embed_hint:  'Each embed is a read-only iframe of a saved view.',
    create_embed_link:  'Leaderboard',
    no_views_embed:    'No saved views yet — go to the Leaderboard page and save a view before creating an embed.',
    lbl_embed_name:    'Embed Name *',
    lbl_saved_view:    'Saved View *',
    btn_gen_embed:     'Generate Embed',
    active_embeds:     'Active Embed Tokens',
    no_embeds:         'No embeds yet.',

    // ── Users ────────────────────────────────────────────
    add_user_title:    'Add User',
    lbl_username:      'Username *',
    lbl_password:      'Password * (min 8 chars)',
    lbl_role:          'Role',
    lbl_language_pref: 'Default Language',
    role_viewer:       'Viewer — read only',
    role_user:         'User — can log own game',
    role_assoc_admin:  'Assoc. Admin — manage association',
    role_admin:        'Admin — full access',
    btn_add_user:      'Add User',
    all_users_title:   'All Users',
    col_username:      'Username',
    col_role:          'Role',
    col_linked_hunter: 'Linked Hunter',
    col_assocs:        'Associations',
    col_status:        'Status',
    col_last_login:    'Last Login',
    col_created:       'Created',
    you_label:         '(you)',
    active_label:      'Active',
    btn_enable:        'Enable',
    btn_disable:       'Disable',

    // ── Associations ─────────────────────────────────────
    create_assoc_title: 'Create Association',
    assoc_placeholder:  'e.g. North Ridge Hunters',
    btn_create:         'Create',
    col_hunters_count:  'hunters',
    col_users_count:    'users',

    // ── Change Password Modal ────────────────────────────
    change_pw_title:   'Change Password',
    lbl_new_pw:        'New Password (min 8 chars)',
    lbl_confirm_pw:    'Confirm Password',
    btn_update_pw:     'Update Password',
    btn_cancel:        'Cancel',

    // ── Save View Modal ──────────────────────────────────
    save_view_title:   'Save This View',
    lbl_view_name:     'View Name',
    view_name_ph:      'e.g. 2024 Moose Season',
    lbl_private:       'Private — only visible to me and admins',
    btn_save:          'Save',

    // ── Edit View Modal ──────────────────────────────────
    edit_view_title:   'Edit View',
    lbl_group_by:      'Group By',
    lbl_chart_type:    'Chart Type',
    lbl_show_labels:   'Show Data Labels',
    lbl_visibility:    'Visibility',
    vis_public:        'Public — visible to all',
    vis_private:       'Private — only me and admins',
    chart_bar:         'Bar',
    chart_hbar:        'Horizontal Bar',
    chart_pie:         'Pie',
    chart_doughnut:    'Doughnut',
    chart_polar:       'Polar Area',
    lbl_on:            'On',
    lbl_off:           'Off',
    btn_save_changes:  'Save Changes',

    // ── Edit Hunter Modal ────────────────────────────────
    edit_hunter_title: 'Edit Hunter',

    // ── Edit Association Modal ───────────────────────────
    edit_assoc_title:  'Edit Association',
    lbl_assoc_hunters: 'Hunters (hold Ctrl/Cmd for multiple)',
    lbl_assoc_users:   'Users',

    // ── Edit User Associations Modal ─────────────────────
    edit_user_assocs_title: 'Associations for',

    // ── Embed Code Modal ─────────────────────────────────
    embed_code_title:  '📡 Embed Code',
    embed_code_hint:   'Copy this snippet into any website.',
    lbl_preview_url:   'Preview URL',
    btn_open:          'Open ↗',
    lbl_iframe_code:   'iframe Code',
    lbl_theme:         'Theme',
    theme_dark:        'Dark',
    theme_light:       'Light',
    theme_transparent: 'Transparent',
    lbl_iframe_size:   'Iframe Size',
    btn_copy_code:     'Copy Code',

    // ── Toast messages ───────────────────────────────────
    toast_hunter_added:   'Hunter added!',
    toast_hunter_updated: 'Hunter updated!',
    toast_hunter_deleted: 'Hunter deleted',
    toast_hunter_unassigned: 'removed from association',
    toast_entry_saved:    'Entry saved!',
    toast_entry_deleted:  'Entry deleted',
    toast_view_saved:     'View saved!',
    toast_view_updated:   'View updated!',
    toast_view_deleted:   'View deleted',
    toast_embed_created:  'Embed created!',
    toast_token_deleted:  'Token deleted',
    toast_token_rotated:  'Token rotated — update your iframe code',
    toast_copied:         'Copied to clipboard!',
    toast_user_created:   'User created!',
    toast_user_deleted:   'User deleted',
    toast_pw_updated:     'Password updated!',
    toast_role_updated:   'Role updated',
    toast_hunter_linked:  'Hunter link updated',
    toast_assoc_created:  'Association created!',
    toast_assoc_updated:  'Association updated!',
    toast_assoc_deleted:  'Association deleted',
    toast_assoc_updated_user: 'Associations updated!',
    toast_view_loaded:    'Loaded view',
    toast_lang_updated:   'Language updated!',
    toast_enabled:        'User enabled',
    toast_disabled:       'User disabled',

    // ── Errors ───────────────────────────────────────────
    err_name_required:    'Name is required.',
    err_fill_required:    'Fill in all required fields',
    err_hunter_exists:    'already exists',
    err_hunter_exists_aa: 'already exists. Ask an admin to assign them to this association.',
    err_no_assoc:         'Select an active association first.',
    err_no_hunter:        'No hunter linked to your account.',
    err_username_pw:      'Username and password required',
    err_username_exists:  'Username already exists',
    err_pw_min:           'Password must be at least 8 characters.',
    err_pw_match:         'Passwords do not match.',
    err_no_embed_name:    'Enter a name for this embed',
    err_no_view:          'Select a saved view',
    err_no_assoc_context: 'Select an active association first.',
    err_reach:            'Could not reach server.',
    err_invalid_login:    'Invalid username or password',
    err_enter_login:      'Enter username and password.',

    // ── Misc ─────────────────────────────────────────────
    no_data:              'No entries found.',
    none_dash:            '—',
    confirm_delete_hunter: 'Delete this hunter and all their game records? This cannot be undone.',
    confirm_delete_user:   'Delete user',
    confirm_delete_view:   'Delete this view?',
    confirm_delete_assoc:  'Delete association',
    confirm_unassign:      'Remove from this association? The hunter will not be deleted.',
    confirm_delete_embed:  'Delete this embed token? The iframe will stop working.',
    confirm_rotate_token:  'Rotate token? The old iframe code will stop working — you will need to update it.',
    lbl_select_view:       '— select a view —',
    lbl_none:              '— none —',
    no_assoc_yet:          'No associations yet.',
    no_users:              'No users.',
    logging_as_prefix:     'Logging as:',
  },

  da: {
    // ── Nav ──────────────────────────────────────────────
    nav_dashboard:     '📊 Oversigt',
    nav_top_list:      '🏆 Topliste',
    nav_log:           '📋 Jagtlog',
    nav_add_entry:     '➕ Tilføj indgang',
    nav_hunters:       '👤 Jægere',
    nav_saved_views:   '🔖 Gemte visninger',
    nav_embeds:        '📡 Indlejring',
    nav_users:         '👥 Brugere',
    nav_associations:  '🏕 Foreninger',

    // ── Header / user menu ───────────────────────────────
    assoc_label:       'Forening',
    all_associations:  'Alle foreninger',
    change_password:   '🔑 Skift adgangskode',
    sign_out:          '↪ Log ud',
    language:          '🌐 Sprog',

    // ── Dashboard ────────────────────────────────────────
    stat_total:        'Samlet vildtbytte',
    stat_hunters:      'Jægere',
    stat_species:      'Dyrearter',
    stat_best:         'Bedste jæger',
    chart_per_hunter:  'Vildtbytte pr. jæger — Oversigt',
    chart_by_species:  'Pr. dyreart',
    recent_entries:    'Seneste indgange',

    // ── Leaderboard ──────────────────────────────────────
    filter_leaderboard: '⚙ Filtrer topliste',
    lbl_hunters:       'Jægere',
    lbl_species:       'Dyrearter',
    lbl_location:      'Sted',
    lbl_year_from:     'År fra',
    lbl_year_to:       'År til',
    lbl_group_by:      'Gruppér efter',
    group_hunter:      'Jæger',
    group_species:     'Dyreart',
    btn_apply:         'Anvend filtre',
    btn_reset:         'Nulstil',
    btn_save_view:     '🔖 Gem denne visning',
    leaderboard_chart: 'Toplistediagram',

    // ── Log ──────────────────────────────────────────────
    filter_log:        '⚙ Filtrer log',
    lbl_hunter:        'Jæger',
    lbl_search:        'Søg',
    btn_filter:        'Filtrer',
    btn_clear:         'Ryd',
    all_entries:       'Alle indgange',
    col_hunter:        'Jæger',
    col_species:       'Dyreart',
    col_count:         'Antal',
    col_date:          'Dato',
    col_location:      'Sted',
    col_notes:         'Noter',

    // ── Add Entry ────────────────────────────────────────
    add_entry_title:   'Tilføj vildtindgang',
    lbl_hunter_req:    'Jæger *',
    lbl_species_req:   'Dyreart *',
    lbl_count_req:     'Antal *',
    lbl_date_req:      'Jagtdato *',
    lbl_location:      'Sted',
    lbl_notes:         'Noter',
    btn_save_entry:    'Gem indgang',
    btn_clear_form:    'Ryd',
    assoc_context:     'Foreningskontekst',
    assoc_hint_admin:  'Filtrer jægerlisten efter forening.',
    assoc_hint_aa:     'Vælg den forening du vil tilføje indgange for.',
    logging_as:        'Logger som',
    no_hunter_linked:  'Din konto er ikke tilknyttet en jæger — kontakt en administrator.',
    adding_for_assoc:  'Tilføjer indgang for foreningens jægere.',

    // ── Hunters ──────────────────────────────────────────
    add_hunter_title:  'Tilføj jæger',
    lbl_name_req:      'Navn *',
    lbl_associations:  'Foreninger',
    btn_add_hunter:    'Tilføj jæger',
    all_hunters_title: 'Alle jægere',
    col_name:          'Navn',
    col_total_game:    'Samlet bytte',
    col_member_since:  'Medlem siden',
    col_assocs:        'Foreninger',
    no_hunters:        'Ingen jægere endnu.',

    // ── Saved Views ──────────────────────────────────────
    saved_views_title: 'Gemte visninger',
    saved_views_hint:  'Opret en visning på Toplistesiden ved at sætte filtre og klikke "Gem denne visning".',
    my_views:          'Mine visninger',
    shared_views:      'Delte visninger',
    shared_views_sub:  '— klik for at anvende, redigering ikke tilgængelig',
    no_views:          'Ingen gemte visninger endnu.',

    // ── Embeds ───────────────────────────────────────────
    create_embed_title: 'Opret indlejring',
    create_embed_hint:  'Hver indlejring er en skrivebeskyttet iframe af en gemt visning.',
    create_embed_link:  'Topsiden',
    no_views_embed:    'Ingen gemte visninger endnu — gå til Topsiden og gem en visning.',
    lbl_embed_name:    'Indlejringsnavn *',
    lbl_saved_view:    'Gemt visning *',
    btn_gen_embed:     'Generér indlejring',
    active_embeds:     'Aktive indlejringstokens',
    no_embeds:         'Ingen indlejringer endnu.',

    // ── Users ────────────────────────────────────────────
    add_user_title:    'Tilføj bruger',
    lbl_username:      'Brugernavn *',
    lbl_password:      'Adgangskode * (min. 8 tegn)',
    lbl_role:          'Rolle',
    lbl_language_pref: 'Standardsprog',
    role_viewer:       'Tilskuer — kun læsning',
    role_user:         'Bruger — kan logge eget bytte',
    role_assoc_admin:  'Foreningsadmin — administrér forening',
    role_admin:        'Administrator — fuld adgang',
    btn_add_user:      'Tilføj bruger',
    all_users_title:   'Alle brugere',
    col_username:      'Brugernavn',
    col_role:          'Rolle',
    col_linked_hunter: 'Tilknyttet jæger',
    col_assocs:        'Foreninger',
    col_status:        'Status',
    col_last_login:    'Seneste login',
    col_created:       'Oprettet',
    you_label:         '(dig)',
    active_label:      'Aktiv',
    btn_enable:        'Aktivér',
    btn_disable:       'Deaktivér',

    // ── Associations ─────────────────────────────────────
    create_assoc_title: 'Opret forening',
    assoc_placeholder:  'f.eks. Nordre Skovjægere',
    btn_create:         'Opret',
    col_hunters_count:  'jægere',
    col_users_count:    'brugere',

    // ── Change Password Modal ────────────────────────────
    change_pw_title:   'Skift adgangskode',
    lbl_new_pw:        'Ny adgangskode (min. 8 tegn)',
    lbl_confirm_pw:    'Bekræft adgangskode',
    btn_update_pw:     'Opdatér adgangskode',
    btn_cancel:        'Annullér',

    // ── Save View Modal ──────────────────────────────────
    save_view_title:   'Gem denne visning',
    lbl_view_name:     'Visningsnavn',
    view_name_ph:      'f.eks. Elgjagt 2024',
    lbl_private:       'Privat — kun synlig for mig og administratorer',
    btn_save:          'Gem',

    // ── Edit View Modal ──────────────────────────────────
    edit_view_title:   'Redigér visning',
    lbl_group_by:      'Gruppér efter',
    lbl_chart_type:    'Diagramtype',
    lbl_show_labels:   'Vis datamærker',
    lbl_visibility:    'Synlighed',
    vis_public:        'Offentlig — synlig for alle',
    vis_private:       'Privat — kun mig og administratorer',
    chart_bar:         'Søjle',
    chart_hbar:        'Vandret søjle',
    chart_pie:         'Cirkel',
    chart_doughnut:    'Donut',
    chart_polar:       'Polarareal',
    lbl_on:            'Til',
    lbl_off:           'Fra',
    btn_save_changes:  'Gem ændringer',

    // ── Edit Hunter Modal ────────────────────────────────
    edit_hunter_title: 'Redigér jæger',

    // ── Edit Association Modal ───────────────────────────
    edit_assoc_title:  'Redigér forening',
    lbl_assoc_hunters: 'Jægere (hold Ctrl/Cmd for flere)',
    lbl_assoc_users:   'Brugere',

    // ── Edit User Associations Modal ─────────────────────
    edit_user_assocs_title: 'Foreninger for',

    // ── Embed Code Modal ─────────────────────────────────
    embed_code_title:  '📡 Indlejringskode',
    embed_code_hint:   'Kopiér dette uddrag ind på et hvilket som helst websted.',
    lbl_preview_url:   'Forhåndsvisnings-URL',
    btn_open:          'Åbn ↗',
    lbl_iframe_code:   'iframe-kode',
    lbl_theme:         'Tema',
    theme_dark:        'Mørkt',
    theme_light:       'Lyst',
    theme_transparent: 'Gennemsigtigt',
    lbl_iframe_size:   'iframe-størrelse',
    btn_copy_code:     'Kopiér kode',

    // ── Toast messages ───────────────────────────────────
    toast_hunter_added:   'Jæger tilføjet!',
    toast_hunter_updated: 'Jæger opdateret!',
    toast_hunter_deleted: 'Jæger slettet',
    toast_hunter_unassigned: 'fjernet fra forening',
    toast_entry_saved:    'Indgang gemt!',
    toast_entry_deleted:  'Indgang slettet',
    toast_view_saved:     'Visning gemt!',
    toast_view_updated:   'Visning opdateret!',
    toast_view_deleted:   'Visning slettet',
    toast_embed_created:  'Indlejring oprettet!',
    toast_token_deleted:  'Token slettet',
    toast_token_rotated:  'Token roteret — opdatér din iframe-kode',
    toast_copied:         'Kopieret til udklipsholder!',
    toast_user_created:   'Bruger oprettet!',
    toast_user_deleted:   'Bruger slettet',
    toast_pw_updated:     'Adgangskode opdateret!',
    toast_role_updated:   'Rolle opdateret',
    toast_hunter_linked:  'Jægertilknytning opdateret',
    toast_assoc_created:  'Forening oprettet!',
    toast_assoc_updated:  'Forening opdateret!',
    toast_assoc_deleted:  'Forening slettet',
    toast_assoc_updated_user: 'Foreninger opdateret!',
    toast_view_loaded:    'Visning indlæst',
    toast_lang_updated:   'Sprog opdateret!',
    toast_enabled:        'Bruger aktiveret',
    toast_disabled:       'Bruger deaktiveret',

    // ── Errors ───────────────────────────────────────────
    err_name_required:    'Navn er påkrævet.',
    err_fill_required:    'Udfyld alle påkrævede felter',
    err_hunter_exists:    'findes allerede',
    err_hunter_exists_aa: 'findes allerede. Bed en administrator om at tildele dem til denne forening.',
    err_no_assoc:         'Vælg en aktiv forening først.',
    err_no_hunter:        'Din konto er ikke tilknyttet en jæger.',
    err_username_pw:      'Brugernavn og adgangskode er påkrævet',
    err_username_exists:  'Brugernavn findes allerede',
    err_pw_min:           'Adgangskoden skal være mindst 8 tegn.',
    err_pw_match:         'Adgangskoderne stemmer ikke overens.',
    err_no_embed_name:    'Indtast et navn til indlejringen',
    err_no_view:          'Vælg en gemt visning',
    err_no_assoc_context: 'Vælg en aktiv forening først.',
    err_reach:            'Serveren er ikke tilgængelig.',
    err_invalid_login:    'Ugyldigt brugernavn eller adgangskode',
    err_enter_login:      'Indtast brugernavn og adgangskode.',

    // ── Misc ─────────────────────────────────────────────
    no_data:              'Ingen indgange fundet.',
    none_dash:            '—',
    confirm_delete_hunter: 'Slet denne jæger og alle deres indgange? Dette kan ikke fortrydes.',
    confirm_delete_user:   'Slet bruger',
    confirm_delete_view:   'Slet denne visning?',
    confirm_delete_assoc:  'Slet forening',
    confirm_unassign:      'Fjern fra denne forening? Jægeren slettes ikke.',
    confirm_delete_embed:  'Slet dette indlejringstoken? iframe\'en holder op med at virke.',
    confirm_rotate_token:  'Rotér token? Den gamle iframe-kode holder op med at virke — du skal opdatere den.',
    lbl_select_view:       '— vælg en visning —',
    lbl_none:              '— ingen —',
    no_assoc_yet:          'Ingen foreninger endnu.',
    no_users:              'Ingen brugere.',
    logging_as_prefix:     'Logger som:',
  }
};

let currentLang = 'en';

function setLang(lang) {
  currentLang = LANGS[lang] ? lang : 'en';
  document.documentElement.lang = currentLang;
  applyTranslations();
}

function t(key) {
  return LANGS[currentLang]?.[key] ?? LANGS['en']?.[key] ?? key;
}

function applyTranslations() {
  // Apply translations to all elements with data-i18n attribute
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    const attr = el.getAttribute('data-i18n-attr');
    if (attr) {
      el.setAttribute(attr, t(key));
    } else {
      el.textContent = t(key);
    }
  });
  // Elements with data-i18n-html (for HTML content)
  document.querySelectorAll('[data-i18n-html]').forEach(el => {
    el.innerHTML = t(el.getAttribute('data-i18n-html'));
  });
}
