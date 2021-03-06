//
//  STEntitySearchController.m
//  Stamped
//
//  Created by Landon Judkins on 4/17/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STEntitySearchController.h"
#import "EntityDetailViewController.h"
#import "STEntitySearchSection.h"
#import "STEntityAutoCompleteResult.h"
#import <CoreLocation/CoreLocation.h>
#import "STImageCache.h"
#import "STTableViewSectionHeader.h"
#import "CreateStampViewController.h"
#import "CreateEntityViewController.h"
#import "UIFont+Stamped.h"
#import "UIColor+Stamped.h"
#import "STNavigationBar.h"
#import "STLoadingCell.h"
#import "NoDataUtil.h"

#define kAddEntityCellTag 101

static const CGFloat _innerBorderHeight = 40;
static const CGFloat _offscreenCancelPadding = 5;

@interface STEntitySearchTableViewCell : UITableViewCell

@property (nonatomic, readwrite, retain) UILabel *titleLabel;
@property (nonatomic, readwrite, retain) UILabel *detailTitleLabel;
@property (nonatomic, readwrite, retain) STCancellation *iconCancellation;
@property (nonatomic, readwrite, retain) UIImageView *iconView;
@property (nonatomic, readwrite, retain) UILabel* distanceLabel;
@property (nonatomic, readwrite, retain) UIImageView* locationImageView;

- (void)setSearchResult:(id<STEntitySearchResult>)searchResult;

@end

@interface STEntitySearchCreateCell : UITableViewCell

@property (nonatomic, readwrite, retain) UILabel *titleLabel;
@property (nonatomic, readwrite, retain) UILabel *detailTitleLabel;

- (id)initWithReuseIdentifier:(NSString *)reuseIdentifier;
- (void)setupWithCategory:(NSString*)category andTitle:(NSString*)title;

@end

@interface STEntitySearchController () <UITableViewDelegate, UITableViewDataSource, UITextFieldDelegate, CLLocationManagerDelegate>

@property (nonatomic, readonly, retain) NSString* category;
@property (nonatomic, readonly, retain) NSString* initialQuery;
@property (nonatomic, readonly, retain) NSMutableArray<STEntityAutoCompleteResult>* autoCompleteResults;
@property (nonatomic, retain) NSArray<STEntitySearchSection>* suggestedSections;
@property (nonatomic, retain) NSArray<STEntitySearchSection>* searchSections;
@property (nonatomic, retain) NSString* coordinates;
@property (nonatomic, retain) STCancellation *autoCompleteCancellation;
@property (nonatomic, retain) STCancellation *searchCancellation;
@property (nonatomic, retain) STCancellation *requestCancellation;
@property (nonatomic, assign) BOOL loading;
@property (nonatomic, retain) CLLocationManager *locationManager;

@end

@implementation STEntitySearchController

@synthesize category = _category;
@synthesize initialQuery = _initialQuery;
@synthesize suggestedSections = _suggestedSections;
@synthesize searchSections = _searchSections;
@synthesize autoCompleteResults = _autoCompleteResults;
@synthesize coordinates = _coordinates;
@synthesize autoCompleteCancellation = _autoCompleteCancellation;
@synthesize requestCancellation = _requestCancellation;
@synthesize searchCancellation = _searchCancellation;
@synthesize loading = _loading;
@synthesize locationManager=_locationManager;

- (id)initWithCategory:(NSString*)category andQuery:(NSString*)query {
    if (self = [super init]) {
        
        if (!category) {
            category = @"music";
        }
        //self.title = [Util titleForCategory:category];
        _category = [category retain];
        _initialQuery = [query retain];
        _autoCompleteResults = (id)[[NSMutableArray alloc] init];
        
    }
    return self;
}

- (void)dealloc {
    [_category release];
    [_initialQuery release];
    [_searchSections release];
    [_suggestedSections release];
    [_autoCompleteResults release];
    [_coordinates release];
    [_requestCancellation cancel];
    [_requestCancellation release];
    [_autoCompleteCancellation cancel];
    [_autoCompleteCancellation release];
    _locationManager.delegate = nil;
    [_locationManager release];
    [super dealloc];
}

- (void)viewDidLoad {
    [super viewDidLoad];
    
    self.showsSearchBar = YES;
    
    /*
     STNavigationItem *button = [[STNavigationItem alloc] initWithTitle:@"Cancel" style:UIBarButtonItemStyleBordered target:self action:@selector(cancel:)];
     self.navigationItem.leftBarButtonItem = button;
     [button release];
     */
    BOOL loadResults = YES;
    CLLocation* location = [STStampedAPI sharedInstance].currentUserLocation;
    if ([_category isEqualToString:@"place"]) {
        _locationManager = [[CLLocationManager alloc] init];
        _locationManager.delegate = self; 
        _locationManager.desiredAccuracy = kCLLocationAccuracyBest; 
        _locationManager.distanceFilter = kCLDistanceFilterNone; 
        [_locationManager startUpdatingLocation];
        location = [_locationManager location];
        if (location) {
            [STStampedAPI sharedInstance].currentUserLocation = location;
            float longitude = location.coordinate.longitude;
            float latitude = location.coordinate.latitude;
            self.coordinates = [NSString stringWithFormat:@"%f,%f", latitude, longitude];
            [_locationManager stopUpdatingLocation];
        }
        else {
            loadResults = NO;
        }
    }
    if (loadResults) {
        [self reloadDataSource];
    }
}

- (void)viewWillAppear:(BOOL)animated {
    [super viewWillAppear:animated];
    NSString* title = [Util titleForCategory:self.category];
    if ([self.category isEqualToString:@"film"]) {
        title = @"Movies & TV";
    }
    [Util setTitle:[NSString stringWithFormat:@"Stamp %@", title]
     forController:self];
    self.tableView.contentOffset = CGPointZero;
}

- (void)viewWillDisappear:(BOOL)animated {
    [super viewWillDisappear:animated];
    [Util setTitle:nil
     forController:self];
    //self.tableView.contentOffset = CGPointZero;
    //[self.navigationController setNavigationBarHidden:NO animated:animated];
}


#pragma mark - CLLocationManagerDelegate

- (void)locationManager:(CLLocationManager *)manager didUpdateToLocation:(CLLocation *)newLocation  fromLocation:(CLLocation *)oldLocation {
    
    float longitude = newLocation.coordinate.longitude;
    float latitude = newLocation.coordinate.latitude;
    self.coordinates = [NSString stringWithFormat:@"%f,%f", latitude, longitude];
    [STStampedAPI sharedInstance].currentUserLocation = newLocation;
    [_locationManager stopUpdatingLocation];
    if (!self.requestCancellation && !self.suggestedSections && !self.searchSections) {
        [self reloadDataSource];
    }
}

- (void)locationManager:(CLLocationManager *)manager didFailWithError:(NSError *)error {
    //[STStampedAPI sharedInstance].currentUserLocation = nil;
    [self reloadDataSource];
    [_locationManager stopUpdatingLocation];
}


#pragma mark - Actions

- (void)backButton:(id)notImportant {
    [Util compareAndPopController:self animated:YES];
}

- (void)cancel:(id)sender {
    
    [self dismissModalViewControllerAnimated:YES];
    
}


#pragma mark - UITableViewDataSource

- (CGFloat)tableView:(UITableView *)tableView heightForRowAtIndexPath:(NSIndexPath *)indexPath {
    if (self.searchCancellation) return tableView.frame.size.height;
    if (tableView == self.searchResultsTableView) {
        
        if (self.autoCompleteResults.count) {
            if (indexPath.row == self.autoCompleteResults.count) {
                return 62.0f;
            }
            return 47;
        }
        
    }
    
    
    
    return 64;
    
}

- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section {
    if (self.searchCancellation) return 1;
    if (tableView == self.searchResultsTableView) {
        
        if (self.autoCompleteResults.count) {
            return self.autoCompleteResults.count;
        }
        
        if (self.searchSections) {
            id<STEntitySearchSection> sectionObject = [self.searchSections objectAtIndex:section];
            return sectionObject.entities.count + 1; // plus one to add 'add' cell
        }
        
        return 1; //1;
        
    }
    
    if (self.suggestedSections) {
        id<STEntitySearchSection> sectionObject = [self.suggestedSections objectAtIndex:section];
        return sectionObject.entities.count;
    }
    
    return 0;
    
    
}

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView {
    if (self.searchCancellation) return 1;
    if (tableView == self.searchResultsTableView) {
        
        if (self.autoCompleteResults.count) {
            return 1;
        }
        
        return self.searchSections ? self.searchSections.count : 1;
        
    }
    
    return self.suggestedSections ? self.suggestedSections.count : 0;
    
}

- (UITableViewCell*)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
    if (self.searchCancellation) {
        return [[[STLoadingCell alloc] init] autorelease];
    }
    if (tableView == self.searchResultsTableView && !self.autoCompleteResults.count) {
        NSInteger count = 0;
        if (self.searchSections) {
            id<STEntitySearchSection> sectionObject = nil;
            if (self.searchSections.count) {
                sectionObject = [self.searchSections objectAtIndex:indexPath.section];
            }
            if (sectionObject && indexPath.row < sectionObject.entities.count) {
                count = sectionObject.entities.count;
            }
            else {
                NSString *AddCellIdentifier = @"AddCellIdentfier";
                STEntitySearchCreateCell* cell = [tableView dequeueReusableCellWithIdentifier:AddCellIdentifier];
                if (!cell) {
                    cell = [[[STEntitySearchCreateCell alloc] initWithReuseIdentifier:AddCellIdentifier] autorelease];
                }
                [cell setupWithCategory:self.category andTitle:self.searchView.text];
                return cell;
            }
        }
        
    }
    
    
    if (tableView == self.searchResultsTableView && self.autoCompleteResults.count) {
        id<STEntityAutoCompleteResult> autoCompleteResult = [self.autoCompleteResults objectAtIndex:indexPath.row];
        static NSString* reuseIdentifier = @"AutoCompleteIdentifier";
        UITableViewCell *cell = [tableView dequeueReusableCellWithIdentifier:reuseIdentifier];
        if (!cell) {
            cell = [[[UITableViewCell alloc] initWithStyle:UITableViewCellStyleDefault reuseIdentifier:reuseIdentifier] autorelease];
        }
        
        cell.textLabel.font = [UIFont stampedBoldFontWithSize:16];
        cell.textLabel.textColor = [UIColor stampedBlackColor];
        cell.textLabel.text = autoCompleteResult.completion;
        cell.indentationWidth = 4.0f;
        cell.indentationLevel = 9;
        
        return cell;
    }
    
    static NSString *CellIdentifier = @"CellIdentifier";
    STEntitySearchTableViewCell* cell = [tableView dequeueReusableCellWithIdentifier:CellIdentifier];
    if (!cell) {
        cell = [[[STEntitySearchTableViewCell alloc] initWithStyle:UITableViewCellStyleDefault reuseIdentifier:CellIdentifier] autorelease];
    }
    
    id<STEntitySearchResult> result = nil;
    
    if (tableView == self.searchResultsTableView) {
        
        if (self.searchSections) {
            id<STEntitySearchSection> section = [self.searchSections objectAtIndex:indexPath.section];
            result = [section.entities objectAtIndex:indexPath.row];
        }
        
    } else {
        
        if (self.suggestedSections) {
            id<STEntitySearchSection> section = [self.suggestedSections objectAtIndex:indexPath.section];
            result = [section.entities objectAtIndex:indexPath.row];
        }
        
    }
    
    cell.searchResult = result;
    return cell;
    
}

- (NSString *)tableView:(UITableView *)tableView titleForHeaderInSection:(NSInteger)section {
    
    if (tableView == self.searchResultsTableView) {
        if (self.searchSections) {
            id<STEntitySearchSection> sectionObject = [self.searchSections objectAtIndex:section];
            return sectionObject.title;
        }
        return nil;
    }
    
    if (self.suggestedSections) {
        id<STEntitySearchSection> sectionObject = [self.suggestedSections objectAtIndex:section];
        return sectionObject.title;
    }
    return nil;
    
    
}

- (CGFloat)tableView:(UITableView*)tableView heightForHeaderInSection:(NSInteger)section {
    if (![self tableView:tableView titleForHeaderInSection:section]) {
        return 0.0f;
    }
    return [STTableViewSectionHeader height];
}

- (UIView*)tableView:(UITableView*)tableView viewForHeaderInSection:(NSInteger)section {
    
    NSString *title = [self tableView:tableView titleForHeaderInSection:section];
    if (title) {
        STTableViewSectionHeader *view = [[STTableViewSectionHeader alloc] initWithFrame:CGRectMake(0.0f, 0.0f, tableView.bounds.size.width, 0)];
        view.titleLabel.text = title;
        if ([self.category isEqualToString:@"place"]) {
            view.googleAttribution = YES;
        }
        return [view autorelease];
    }
    return nil;
    
}


#pragma mark - UITableViewDelegate

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
    if (self.searchCancellation) return;
    BOOL add = NO;
    if (tableView == self.searchResultsTableView) {
        
        NSInteger count = 0;
        if (self.autoCompleteResults.count) {
            count = self.autoCompleteResults.count;
        } else if (self.searchSections && indexPath.section < self.searchSections.count) {
            if (indexPath.section < self.searchSections.count) {
                id<STEntitySearchSection> sectionObject = [self.searchSections objectAtIndex:indexPath.section];
                if ([sectionObject entities].count == 0) {
                    add = YES;
                }
                else if (indexPath.row >= [sectionObject entities].count) {
                    add = YES;
                }
            }
            else {
                add = YES;
            }
        }
        else {
            add = YES;
        }
        
    }
    if (add) {
        CreateEntityViewController *controller = [[[CreateEntityViewController alloc] initWithEntityCategory:self.category entityTitle:self.searchView.text] autorelease];
        [Util pushController:controller modal:NO animated:YES];
        return;
    }
    
    if (self.autoCompleteResults.count) {
        
        if (self.autoCompleteResults.count > indexPath.row) {
            id<STEntityAutoCompleteResult> autoCompleteResult = [self.autoCompleteResults objectAtIndex:indexPath.row];
            [self.searchView setText:autoCompleteResult.completion];
            [self.searchView resignKeyboard];
            [self performSearchWithText:autoCompleteResult.completion];
        }
    } else {
        
        id<STEntitySearchResult> result = nil;
        
        if (tableView == self.searchResultsTableView && self.searchSections) {
            id<STEntitySearchSection> section = [self.searchSections objectAtIndex:indexPath.section];
            result = [section.entities objectAtIndex:indexPath.row];
        } else if (self.suggestedSections) {
            id<STEntitySearchSection> section = [self.suggestedSections objectAtIndex:indexPath.section];
            result = [section.entities objectAtIndex:indexPath.row];
        }
        
        CreateStampViewController *controller = [[CreateStampViewController alloc] initWithSearchResult:result];
        [self.navigationController pushViewController:controller animated:YES];
        [controller release];
        
    }
    
}


#pragma mark STSearchViewDelegate

- (void)performSearchWithText:(NSString*)text {
    
    [self.searchCancellation cancel];
    self.searchCancellation = nil;
    [self.autoCompleteCancellation cancel];
    self.autoCompleteCancellation = nil;
    [self.autoCompleteResults removeAllObjects];
    [self.searchResultsTableView reloadData];
    [self.searchView setLoading:YES];
    
    STEntitySearch *search = [[[STEntitySearch alloc] init] autorelease];
    search.category = self.category;
    search.query = text;
    search.coordinates = self.coordinates;
    self.searchSections = nil;
    self.searchCancellation = [[STStampedAPI sharedInstance] entityResultsForEntitySearch:search andCallback:^(NSArray<STEntitySearchSection> *sections, NSError *error, STCancellation* cancellation) {
        
        [self.searchView setLoading:NO];
        self.searchCancellation = nil;
        if (sections) {
            self.searchSections = sections;
            [self.searchResultsTableView reloadData];
        }
        
    }];
    [self.searchResultsTableView reloadData];
}

- (void)stSearchViewHitSearch:(STSearchView*)view withText:(NSString*)text {
    
    [self performSearchWithText:text];
    
}

- (void)stSearchView:(STSearchView*)view textDidChange:(NSString*)text {
    
    [super stSearchView:view textDidChange:text];
    [self.autoCompleteCancellation cancel];
    self.autoCompleteCancellation = nil;
    
    if (!text || [text stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceCharacterSet]].length <= 1) {
        return;
    }
    
    [self.searchView setLoading:YES];
    self.autoCompleteCancellation = [[STStampedAPI sharedInstance] entityAutocompleteResultsForQuery:text coordinates:self.coordinates category:self.category andCallback:^(NSArray<STEntityAutoCompleteResult> *results, NSError *error, STCancellation *cancellation) {
        
        self.autoCompleteCancellation = nil;
        [self.autoCompleteResults removeAllObjects];
        if (results.count) {
            [self.autoCompleteResults addObjectsFromArray:results];
        }
        [self.searchResultsTableView reloadData];
        [self.searchView setLoading:NO];
        
    }];
    
    UITableViewCell *cell = (UITableViewCell*)[self.searchResultsTableView viewWithTag:kAddEntityCellTag];
    if (cell) {
        [cell.detailTextLabel setText:[NSString stringWithFormat:@"add the %@ \"%@\"", self.category, text]];
    }
    
}

- (void)stSearchViewDidCancel:(STSearchView*)view {
    [super stSearchViewDidCancel:view];
    [self.searchCancellation cancel];
    self.searchCancellation = nil;
    [self.autoCompleteCancellation cancel];
    self.autoCompleteCancellation = nil;
    
}


#pragma mark - STRestController

- (BOOL)dataSourceReloading {
    return _loading;
}

- (void)loadNextPage {
}

- (BOOL)dataSourceHasMoreData {
    return NO;
}

- (void)reloadDataSource {
    if (_loading) return; 
    _loading = YES;
    
    STEntitySuggested* suggested = [[[STEntitySuggested alloc] init] autorelease];
    suggested.coordinates = self.coordinates;
    suggested.category = self.category;
    
    self.requestCancellation = [[STStampedAPI sharedInstance] entityResultsForEntitySuggested:suggested  andCallback:^(NSArray<STEntitySearchSection> *results, NSError *error, STCancellation* cancellation) {
        
        NSInteger sections = [self.tableView numberOfSections];
        self.requestCancellation = nil;
        if (results) {
            self.suggestedSections = results;
            
            if (sections == 0 && self.suggestedSections) {
                
                [self.tableView beginUpdates];
                [self.tableView insertSections:[NSIndexSet indexSetWithIndexesInRange:NSMakeRange(0, self.suggestedSections.count)] withRowAnimation:UITableViewRowAnimationFade];
                [self.tableView endUpdates];
                
            } else {
                
                [self.tableView reloadData];
                
            }
            
        }
        
        _loading = NO;
        [self dataSourceDidFinishLoading];
        if (sections==0) {
            //[self animateIn];
        }
        
    }];
    [super reloadDataSource];
    
}

- (BOOL)dataSourceIsEmpty {
    return (self.suggestedSections.count==0);
}

- (void)setupNoDataView:(NoDataView*)view {
    
    view.custom = YES;
    
    UIView* waterMark = [NoDataUtil waterMarkWithImage:nil
                                                 title:@"No Suggestions" 
                                                  body:@"Try searching for what you're looking for."
                                               options:nil];
    waterMark.frame = [Util centeredAndBounded:waterMark.frame.size inFrame:CGRectMake(0, -50, view.frame.size.width, view.frame.size.height)];
    [view addSubview:waterMark];
    //    CGRect frame = view.frame;
    //    CGFloat height = self.tableView.tableHeaderView.bounds.size.height;
    //    frame.origin.y = height;
    //    frame.size.height -= height;
    //    view.frame = frame;
    //    [view setupWithTitle:@"No Suggestions" detailTitle:@"No suggestions found."];
    
}

@end


#pragma mark - STEntitySearchTableViewCell

@implementation STEntitySearchTableViewCell

@synthesize titleLabel = _titleLabel;
@synthesize detailTitleLabel = _detailTitleLabel;
@synthesize iconCancellation = _iconCancellation;
@synthesize iconView = _iconView;
@synthesize distanceLabel = _distanceLabel;
@synthesize locationImageView = _locationImageView;

- (id)initWithStyle:(UITableViewCellStyle)style reuseIdentifier:(NSString *)reuseIdentifier {
    if ((self = [super initWithStyle:UITableViewCellStyleDefault reuseIdentifier:reuseIdentifier])) {
        
        UIImageView *imageView = [[UIImageView alloc] initWithFrame:CGRectMake(12, 17, 16, 16)];
        imageView.contentMode = UIViewContentModeScaleAspectFit;
        [self.contentView addSubview:imageView];
        _iconView = [imageView retain];
        [imageView release];
        
        UIFont *font = [UIFont stampedTitleFontWithSize:24];
        UILabel *label = [[UILabel alloc] initWithFrame:CGRectMake(36.0f, 12.0f, 0.0f, font.lineHeight)];
        label.textColor = [UIColor stampedBlackColor];
        label.highlightedTextColor = [UIColor whiteColor];
        label.font = font;
        label.backgroundColor = [UIColor whiteColor];
        [self addSubview:label];
        _titleLabel = [label retain];
        [label release];
        
        font = [UIFont stampedFontWithSize:12];
        label = [[UILabel alloc] initWithFrame:CGRectMake(36.0f, CGRectGetMaxY(_titleLabel.frame)-2.0f, 0.0f, font.lineHeight)];
        label.textColor = [UIColor stampedGrayColor];
        label.highlightedTextColor = [UIColor whiteColor];
        label.font = font;
        label.backgroundColor = [UIColor whiteColor];
        [self addSubview:label];
        _detailTitleLabel = [label retain];
        [label release];
        
        _distanceLabel = [[UILabel alloc] initWithFrame:CGRectZero];
        _distanceLabel.backgroundColor = [UIColor clearColor];
        _distanceLabel.textColor = [UIColor stampedLightGrayColor];
        _distanceLabel.highlightedTextColor = [UIColor whiteColor];
        _distanceLabel.font = [UIFont fontWithName:@"Helvetica-Bold" size:10];
        [self.contentView addSubview:_distanceLabel];
        
        UIImage* locationImage = [UIImage imageNamed:@"small_location_icon"];
        UIImage* highlightedLocationImage = [Util whiteMaskedImageUsingImage:locationImage];
        _locationImageView = [[UIImageView alloc] initWithImage:locationImage
                                               highlightedImage:highlightedLocationImage];
        [self.contentView addSubview:_locationImageView];
    }
    return self;
}

- (void)layoutSubviews {
    [super layoutSubviews];
    
    [_titleLabel sizeToFit];
    [_detailTitleLabel sizeToFit];
    
    CGRect frame = _titleLabel.frame;
    frame.size.width = MIN(self.bounds.size.width - 40.0f, frame.size.width);
    _titleLabel.frame = frame;
    
    frame = _detailTitleLabel.frame;
    frame.size.width = MIN(self.bounds.size.width - 40.0f, frame.size.width);
    _detailTitleLabel.frame = frame;
    
}

- (void)dealloc {
    [_iconCancellation cancel];
    [_iconCancellation release];
    [_iconView release];
    [_detailTitleLabel release];
    [_titleLabel release];
    [_distanceLabel release];
    [_locationImageView release];
    [super dealloc];
}

- (void)setSearchResult:(id<STEntitySearchResult>)searchResult {
    self.iconView.image = nil;
    
    _titleLabel.text = searchResult.title;
    _detailTitleLabel.text = searchResult.subtitle;
    
    [self.iconCancellation cancel];
    self.iconCancellation = nil;
    NSString* iconURL = searchResult.icon;
    if (iconURL) {
        
        UIImage *icon = [[STImageCache sharedInstance] cachedImageForImageURL:iconURL];
        if (icon) {
            dispatch_async(dispatch_get_main_queue(), ^{
                self.iconView.image = icon;
            });
        }
        else {
            self.iconCancellation = [[STImageCache sharedInstance] imageForImageURL:iconURL andCallback:^(UIImage *image, NSError *error, STCancellation *cancellation) {
                if (image) {
                    self.iconView.image = image;
                }
                self.iconCancellation = nil;
            }];
        }
    }
    
    if (searchResult.distance) {
        CGFloat miles = searchResult.distance.floatValue;
        if (miles < 2.0) {
            self.distanceLabel.textColor = [UIColor colorWithRed:0.66 green:0.48 blue:0.8 alpha:1.0];
            self.locationImageView.image = [UIImage imageNamed:@"small_location_icon_purple"];
        }
        else {
            self.distanceLabel.textColor = [UIColor stampedLightGrayColor];
            self.locationImageView.image = [UIImage imageNamed:@"small_location_icon"];
        }
        if (miles > 0.1) {
            self.distanceLabel.text = [NSString stringWithFormat:@"%.1f mi", miles];
        }
        else {
            self.distanceLabel.text = [NSString stringWithFormat:@"%.0f ft", miles * 5280.0f];
        }
        
        [self.distanceLabel sizeToFit];
        CGRect distanceFrame = self.distanceLabel.frame;
        distanceFrame.origin.x = 311 - distanceFrame.size.width;
        distanceFrame.origin.y = 22;
        self.distanceLabel.frame = distanceFrame;
        self.locationImageView.frame = CGRectMake(CGRectGetMinX(distanceFrame) - CGRectGetWidth(self.locationImageView.frame) - 3,
                                              CGRectGetMinY(distanceFrame) + 2, 
                                              CGRectGetWidth(self.locationImageView.frame),
                                              CGRectGetHeight(self.locationImageView.frame));
        self.distanceLabel.hidden = NO;
        self.locationImageView.hidden = NO;
    }
    else {
        self.distanceLabel.hidden = YES;
        self.locationImageView.hidden = YES;
    }
    
}

@end

@implementation STEntitySearchCreateCell

@synthesize titleLabel = _titleLabel;
@synthesize detailTitleLabel = _detailTitleLabel;

- (id)initWithReuseIdentifier:(NSString *)reuseIdentifier {
    self = [super initWithStyle:UITableViewCellStyleSubtitle reuseIdentifier:reuseIdentifier];
    if (self) {
        UIFont *font = [UIFont stampedBoldFontWithSize:14];
        UILabel *label = [[[UILabel alloc] initWithFrame:CGRectMake(36.0f, 14.0f, 0.0f, font.lineHeight)] autorelease];
        label.textColor = [UIColor stampedDarkGrayColor];
        label.highlightedTextColor = [UIColor whiteColor];
        label.font = font;
        label.backgroundColor = [UIColor whiteColor];
        [self.contentView addSubview:label];
        _titleLabel = [label retain];
        
        UIFont* subtitleFont = [UIFont stampedFontWithSize:12];
        label = [[[UILabel alloc] initWithFrame:CGRectMake(36.0f, CGRectGetMaxY(_titleLabel.frame)-2.0f, 0.0f, subtitleFont.lineHeight)] autorelease];
        label.textColor = [UIColor stampedGrayColor];
        label.highlightedTextColor = [UIColor whiteColor];
        label.font = subtitleFont;
        label.backgroundColor = [UIColor whiteColor];
        [self.contentView addSubview:label];
        _detailTitleLabel = [label retain];
    }
    return self;
}

- (void)setupWithCategory:(NSString *)category andTitle:(NSString *)title {
    self.titleLabel.text = @"Not found?";
    [self.titleLabel sizeToFit];
    self.detailTitleLabel.text = [NSString stringWithFormat:@"Add \"%@\"", title];
    [self.detailTitleLabel sizeToFit];
}

- (void)dealloc
{
    [_detailTitleLabel release];
    [_titleLabel release];
    [super dealloc];
}

@end


