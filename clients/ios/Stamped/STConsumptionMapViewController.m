//
//  STConsumptionMapViewController.m
//  Stamped
//
//  Created by Landon Judkins on 5/7/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STConsumptionMapViewController.h"
#import "STConsumptionToolbar.h"
#import "STSearchField.h"
#import <MapKit/MapKit.h>
#import "STConfiguration.h"
#import <math.h>
#import "Util.h"
#import "STStampedActions.h"
#import "UserImageView.h"
#import "STActionManager.h"
#import "STEntityAnnotation.h"
#import "STPreviewsView.h"

static NSString* const _cacheOverlayKey = @"Consumption.food.cacheOverlay";

static NSString* const _restaurantNameKey = @"Consumption.food.restaurants.name";
static NSString* const _restaurantIconKey = @"Consumption.food.restaurants.icon";
static NSString* const _restaurantBackIconKey = @"Consumption.food.restaurants.backIcon";

static NSString* const _barNameKey = @"Consumption.food.bar.name";
static NSString* const _barIconKey = @"Consumption.food.bar.icon";
static NSString* const _barBackIconKey = @"Consumption.food.bar.backIcon";

static NSString* const _cafeNameKey = @"Consumption.food.cafe.name";
static NSString* const _cafeIconKey = @"Consumption.food.cafe.icon";
static NSString* const _cafeBackIconKey = @"Consumption.food.cafe.backIcon";

static NSString* const _subcategoryType = @"subcategory";
static NSString* const _filterType = @"filter";

const CGFloat _standardLatLongSpan = 600.0f / 111000.0f;

typedef struct STTileRect {
NSInteger x;
NSInteger y;
NSInteger width;
NSInteger height;
NSInteger zoom;
} STTileRect;

@interface STConsumptionMapTile : NSObject <MKOverlay, NSCoding>

- (id)initWithX:(NSInteger)x y:(NSInteger)y andZoom:(NSInteger)zoom;

+ (NSString*)keyForX:(NSInteger)x y:(NSInteger)y andZoom:(NSInteger)zoom;

@property (nonatomic, readonly, assign) NSInteger x;
@property (nonatomic, readonly, assign) NSInteger y;
@property (nonatomic, readonly, assign) NSInteger zoom;
@property (nonatomic, readonly, retain) NSMutableDictionary* entities;
@property (nonatomic, readonly, copy) NSString* key;

@end

@interface STConsumptionMapTileView : MKOverlayView

- (id)initWithMapTile:(STConsumptionMapTile*)tile;

@property (nonatomic, readonly, retain) STConsumptionMapTile* tile;

@end

@interface STConsumptionMapCache : NSObject

- (id)initWithSubcategory:(NSString*)subcategory 
                    scope:(STStampedAPIScope)scope 
                   filter:(NSString*)filter 
                    query:(NSString*)query;

- (NSArray*)cachedTilesForRegion:(MKCoordinateRegion)region;

- (STCancellation*)entitiesForRegion:(MKCoordinateRegion)region
                         andCallback:(void (^)(NSArray<STEntityDetail>* entities, NSError* error, STCancellation* cancellation))block;

+ (NSString*)keyForSubcategory:(NSString*)subcategory
                         scope:(STStampedAPIScope)scope 
                        filter:(NSString*)filter
                         query:(NSString*)query;

+ (void)componentsForKey:(NSString*)key 
             subcategory:(NSString**)subcategory 
                   scope:(STStampedAPIScope*)scope 
                  filter:(NSString**)filter 
                   query:(NSString**)query;

@property (nonatomic, readonly, copy) NSString* key;
@property (nonatomic, readonly, assign) STStampedAPIScope scope;
@property (nonatomic, readonly, retain) NSString* subcategory;
@property (nonatomic, readonly, retain) NSString* query;
@property (nonatomic, readonly, retain) NSString* filter;
@property (nonatomic, readonly, retain) NSCache* cache;

@end

@interface STConsumptionMapViewController () <MKMapViewDelegate, STConsumptionToolbarDelegate>

- (void)update;

@property (nonatomic, readonly, retain) STConsumptionToolbar* consumptionToolbar;
@property (nonatomic, readonly, retain) STSearchField* searchField;
@property (nonatomic, readonly, retain) UIView* previewContainer;
@property (nonatomic, readonly, retain) STPreviewsView* previews;
@property (nonatomic, readonly, retain) MKMapView* mapView;
@property (nonatomic, readwrite, assign) BOOL zoomToUserLocation;
@property (nonatomic, readwrite, assign) MKMapRect lastMapRect;
@property (nonatomic, readonly, retain) NSMutableDictionary* caches;
@property (nonatomic, readwrite, assign) STStampedAPIScope scope;
@property (nonatomic, readwrite, copy) NSString* subcategory;
@property (nonatomic, readwrite, copy) NSString* filter;
@property (nonatomic, readwrite, copy) NSString* query;
@property (nonatomic, readonly, retain) NSMutableArray* annotations;
@property (nonatomic, readonly, retain) NSMutableArray* cancellations;
@property (nonatomic, readonly, retain) NSMutableArray* tileOverlays;
@property (nonatomic, readwrite, assign) BOOL cachingDisabled;
@property (nonatomic, readonly, assign) CGRect previewContainerFrameHidden;
@property (nonatomic, readonly, assign) CGRect previewContainerFrameShown;

@end

@implementation STConsumptionMapViewController

@synthesize consumptionToolbar = consumptionToolbar_;
@synthesize searchField = searchField_;
@synthesize mapView = mapView_;
@synthesize zoomToUserLocation = zoomToUserLocation_;
@synthesize lastMapRect = lastMapRect_;
@synthesize caches = caches_;
@synthesize scope = scope_;
@synthesize subcategory = subcategory_;
@synthesize filter = filter_;
@synthesize query = query_;
@synthesize annotations = annotations_;
@synthesize cancellations = cancellations_;
@synthesize cachingDisabled = cachingDisabled_;
@synthesize tileOverlays = tileOverlays_;
@synthesize previewContainer = _previewContainer;
@synthesize previews = _previews;
@synthesize previewContainerFrameShown = _previewContainerFrameShown;
@synthesize previewContainerFrameHidden = _previewContainerFrameHidden;

- (STConsumptionToolbarItem*)rootItem {
    STConsumptionToolbarItem* item = [[STConsumptionToolbarItem alloc] init];
    
    STConsumptionToolbarItem* restaurants = [[[STConsumptionToolbarItem alloc] init] autorelease];
    restaurants.name = [STConfiguration value:_restaurantNameKey];
    restaurants.icon = [STConfiguration value:_restaurantIconKey];
    restaurants.backIcon = [STConfiguration value:_restaurantBackIconKey];
    restaurants.value = @"restaurant";
    restaurants.type = _subcategoryType;
    
    STConsumptionToolbarItem* bars = [[[STConsumptionToolbarItem alloc] init] autorelease];
    bars.name = [STConfiguration value:_barNameKey];
    bars.icon = [STConfiguration value:_barIconKey];
    bars.backIcon = [STConfiguration value:_barBackIconKey];
    bars.value = @"bar";
    bars.type = _subcategoryType;
    
    STConsumptionToolbarItem* cafe = [[[STConsumptionToolbarItem alloc] init] autorelease];
    cafe.name = [STConfiguration value:_cafeNameKey];
    cafe.icon = [STConfiguration value:_cafeIconKey];
    cafe.backIcon = [STConfiguration value:_cafeBackIconKey];
    cafe.value = @"cafe";
    cafe.type = _subcategoryType;
    
    item.children = [NSArray arrayWithObjects:
                     restaurants, 
                     bars,
                     cafe,
                     nil];
    return item;
}

- (id)init
{
    self = [super init];
    if (self) {
        consumptionToolbar_ = [[STConsumptionToolbar alloc] initWithRootItem:[self rootItem] andScope:STStampedAPIScopeFriends];
        caches_ = [[NSMutableDictionary alloc] init];
        scope_ = STStampedAPIScopeFriends;
        annotations_ = [[NSMutableArray alloc] init];
        cancellations_ = [[NSMutableArray alloc] init];
        tileOverlays_ = [[NSMutableArray alloc] init];
    }
    return self;
}

- (void)dealloc
{
    // Release any retained subviews of the main view.
    consumptionToolbar_.slider.delegate = nil;
    searchField_.delegate = nil;
    [searchField_ release];
    mapView_.delegate = nil;
    [mapView_ release];
    [caches_ release];
    [consumptionToolbar_ release];
    [subcategory_ release];
    [filter_ release];
    [query_ release];
    [tileOverlays_ release];
    [cancellations_ release];
    [annotations_ release];
    [_previews release];
    [_previewContainer release];
    [super dealloc];
}

- (void)viewDidLoad
{
    [super viewDidLoad];
    self.consumptionToolbar.slider.delegate = (id<STSliderScopeViewDelegate>)self;
    self.consumptionToolbar.delegate = self;
    self.zoomToUserLocation = YES;
    UIView* searchBar = [[[UIView alloc] initWithFrame:CGRectMake(0, 0, 320, 40)] autorelease];
    searchField_ = [[STSearchField alloc] initWithFrame:CGRectMake(10, 5, 300, 30)];
    searchField_.placeholder = @"Search for places";
    searchField_.enablesReturnKeyAutomatically = NO;
    searchField_.delegate = self;
    [searchBar addSubview:searchField_];
    searchBar.backgroundColor = [UIColor colorWithWhite:.9 alpha:1];
    [self.scrollView appendChildView:searchBar];
	// Do any additional setup after loading the view.
    mapView_ = [[MKMapView alloc] initWithFrame:CGRectMake(0,
                                                           0,
                                                           self.scrollView.frame.size.width,
                                                           self.scrollView.contentSize.height - CGRectGetMaxY(searchBar.frame))];
    [self.scrollView appendChildView:mapView_];
    _previewContainerFrameHidden = CGRectMake(0, CGRectGetMaxY(mapView_.frame), 320, 44);
    _previewContainerFrameShown = CGRectOffset(_previewContainerFrameHidden, 0, -_previewContainerFrameHidden.size.height);
    _previewContainer = [[UIView alloc] initWithFrame:_previewContainerFrameHidden];
    [Util addGradientToLayer:_previewContainer.layer withColors:[UIColor stampedLightGradient] vertical:YES];
    _previews = [[STPreviewsView alloc] initWithFrame:CGRectMake(0, 0, 0, 0)];
    [_previewContainer addSubview:_previews];
    [self.scrollView addSubview:_previewContainer];
    mapView_.delegate = self;
    //[Util addConfigurationButtonToController:self];
    [self update];
}

- (void)viewDidAppear:(BOOL)animated {
    mapView_.showsUserLocation = YES;
}

- (void)viewWillDisappear:(BOOL)animated {
    for (STCancellation* cancellation in self.cancellations) {
        [cancellation cancel];
    }
}

- (void)viewDidUnload
{
    [super viewDidUnload];
}

- (UIView *)loadToolbar {
    return self.consumptionToolbar;
}


#pragma mark - MKMapViewDelegate Methods

- (void)zoomToCurrentLocation {
    CLLocationCoordinate2D currentLocation = mapView_.userLocation.location.coordinate;
    MKCoordinateSpan mapSpan = MKCoordinateSpanMake(_standardLatLongSpan, _standardLatLongSpan);
    MKCoordinateRegion region = MKCoordinateRegionMake(currentLocation, mapSpan);
    [mapView_ setRegion:region animated:YES];
}

- (void)mapView:(MKMapView*)mapView didUpdateUserLocation:(MKUserLocation*)userLocation {
    if (self.zoomToUserLocation) {
        [self zoomToCurrentLocation];
        self.zoomToUserLocation = NO;
    }
}

+ (CGFloat)tileSizeWithZoomLevel:(NSInteger)zoomLevel {
    //TODO optimize
    CGFloat tileSize = 1;
    while (zoomLevel < 0) {
        tileSize /= 2;
        zoomLevel++;
    }
    while (zoomLevel > 0) {
        tileSize *= 2;
        zoomLevel--;
    }
    return tileSize;
}

+ (NSInteger)zoomLevelWithRegion:(MKCoordinateRegion)region {
    //TODO optimize
    CGFloat tileHeight = 1.5;
    NSInteger zoomLevel = 0;
    CGFloat span = region.span.latitudeDelta / tileHeight;
    CGFloat tileSize = 1;
    if (span < tileSize) {
        //negative levels
        while (span < tileSize) {
            tileSize /= 2;
            zoomLevel--;
        }
    }
    else {
        //positive levels
        while (span > tileSize * 2) {
            tileSize *= 2;
            zoomLevel++;
        }
    }
    //NSLog(@"tile size: %f", tileSize);
    return zoomLevel;
}

+ (STTileRect)tileOriginWithPoint:(CGPoint)point andZoom:(NSInteger)zoom {
    CGFloat tileSize = [STConsumptionMapViewController tileSizeWithZoomLevel:zoom];
    CGFloat latCorner = point.y;
    NSInteger y = floor(latCorner / tileSize);
    CGFloat lonCorner = point.x;
    NSInteger x = floor(lonCorner / tileSize);
    STTileRect rect;
    rect.x = x;
    rect.y = y;
    rect.zoom = zoom;
    rect.width = 0;
    rect.height = 0;
    return rect;
}

+ (STTileRect)tileFrameWithRegion:(MKCoordinateRegion)region withZoom:(NSInteger)zoom {
    CGPoint lonLat = CGPointMake(region.center.longitude - ( region.span.longitudeDelta / 2 ), region.center.latitude - ( region.span.latitudeDelta / 2 ));
    STTileRect tileRect = [self tileOriginWithPoint:lonLat andZoom:zoom];
    CGFloat tileSize = [self tileSizeWithZoomLevel:zoom];
    //TODO improve
    tileRect.width = ceil( region.span.longitudeDelta / tileSize ) + 1;
    tileRect.height = ceil( region.span.latitudeDelta / tileSize ) + 1;
    return tileRect;
}

+ (STTileRect)tileFrameWithRegion:(MKCoordinateRegion)region {
    NSInteger zoom = [self zoomLevelWithRegion:region];
    return [self tileFrameWithRegion:region withZoom:zoom];
}

+ (CGRect)coordinateFrame:(STTileRect)frame {
    CGFloat tileSize = [STConsumptionMapViewController tileSizeWithZoomLevel:frame.zoom];
    return CGRectMake(frame.x * tileSize, frame.y * tileSize, tileSize * frame.width, tileSize * frame.height);
}

+ (NSSet*)tileKeysForTileFrame:(STTileRect)tileFrame {
    NSMutableSet* set = [NSMutableSet set];
    for (NSInteger x = 0; x < tileFrame.width; x++) {
        for (NSInteger y = 0; y < tileFrame.height; y++) {
            [set addObject:[STConsumptionMapTile keyForX:tileFrame.x + x y:tileFrame.y + y andZoom:tileFrame.zoom]];
        }
    }
    return set;
}

- (void)mapView:(MKMapView*)mapView regionDidChangeAnimated:(BOOL)animated {
    
    // Calculate delta of origins across longitudinal distance.
    //CGFloat originDelta = MKMetersBetweenMapPoints(lastMapRect_.origin, mapView.visibleMapRect.origin);
    //MKMapPoint upperRight = MKMapPointMake(MKMapRectGetMaxX(lastMapRect_), MKMapRectGetMinY(lastMapRect_));
    //CGFloat span = MKMetersBetweenMapPoints(lastMapRect_.origin, upperRight);
    
    //NSLog(@"%d",[self zoomLevel]);
    //if ((originDelta / span) < kMapSpanHysteresisPercentage)
    //return;
    
    //if (searchField_.text.length > 0)
    //return;
    //lastMapRect_ = mapView.visibleMapRect;
    //MKCoordinateRegion region = self.mapView.region;
    //NSLog(@"%f,%f,%f,%f",region.center.latitude, region.center.longitude, region.span.latitudeDelta, region.span.longitudeDelta);
    
    //CGRect frame = [self tileFrame];
    ///NSLog(@"frame:%f,%f,%f,%f", frame.origin.x, frame.origin.y, frame.size.width, frame.size.height);
    //[self resetCaches];
    //[self loadDataFromNetwork];
    [self update]; 
}



- (void)mapDisclosureTapped:(id)sender {
    UIButton* disclosureButton = sender;
    UIView* view = [disclosureButton superview];
    while (view && ![view isMemberOfClass:[MKPinAnnotationView class]])
        view = [view superview];
    
    if (!view)
        return;
    
    STEntityAnnotation* annotation = (STEntityAnnotation*)[(MKPinAnnotationView*)view annotation];
    id<STEntityDetail> entityDetail = annotation.entityDetail;
    if (entityDetail) {
        STActionContext* context = [STActionContext context];
        id<STAction> action = [STStampedActions actionViewEntity:entityDetail.entityID withOutputContext:context];
        context.entityDetail = entityDetail;
        [[STActionManager sharedActionManager] didChooseAction:action withContext:context];
    }
}
/*
 - (void)viewUser:(id<STUser>)user {
 //NSLog(@"view user");
 [[STStampedActions sharedInstance] viewUserWithUserID:user.userID];
 }
 */
/*
 - (void)mapUserTapped:(id)sender {
 UserImageView* userImage = sender;
 UIView* view = [userImage superview];
 while (view && ![view isMemberOfClass:[MKPinAnnotationView class]])
 view = [view superview];
 
 if (!view)
 return;
 
 STEntityAnnotation* annotation = (STConsumptionAnnotation*)[(MKPinAnnotationView*)view annotation];
 [[STStampedActions sharedInstance] viewUserWithUserID:annotation.stamp.user.userID];
 }
 */

- (MKAnnotationView*)mapView:(MKMapView*)theMapView viewForAnnotation:(id<MKAnnotation>)annotation {
    if (![annotation isKindOfClass:[STEntityAnnotation class]])
        return nil;
    
    MKPinAnnotationView* pinView = [[[MKPinAnnotationView alloc] initWithAnnotation:annotation reuseIdentifier:nil] autorelease];
    UIButton* disclosureButton = [UIButton buttonWithType:UIButtonTypeDetailDisclosure];
    [disclosureButton addTarget:self
                         action:@selector(mapDisclosureTapped:)
               forControlEvents:UIControlEventTouchUpInside];
    pinView.rightCalloutAccessoryView = disclosureButton;
    pinView.pinColor = MKPinAnnotationColorRed;
    pinView.canShowCallout = YES;
    
    id<STEntityDetail> entity = [(STEntityAnnotation*)annotation entityDetail];
    if (entity) {
        /*
         UserImageView* userImageView = [[UserImageView alloc] initWithFrame:CGRectMake(0, 0, STProfileImageSize31, STProfileImageSize31)];
         userImageView.enabled = YES;
         [userImageView addTarget:self
         action:@selector(mapUserTapped:)
         forControlEvents:UIControlEventTouchUpInside];
         userImageView.imageURL = [Util profileImageURLForUser:stamp.user withSize:STProfileImageSize31];
         pinView.leftCalloutAccessoryView = userImageView;
         */
    }
    
    return pinView;
}

- (void)mapView:(MKMapView *)mapView didSelectAnnotationView:(MKAnnotationView *)view {
    if (![view.annotation isKindOfClass:[STEntityAnnotation class]])
        return;
    STEntityAnnotation* annotation = (id)view.annotation;
    id<STPreviews> preview = annotation.entityDetail.previews;
    if (preview) {
        [self.previews setupWithPreview:preview maxRows:1];
        self.previews.frame = [Util centeredAndBounded:self.previews.frame.size 
                                               inFrame:CGRectMake(0, 0, self.previewContainer.frame.size.width, self.previewContainer.frame.size.height)];
        [UIView animateWithDuration:.25 delay:0 options:UIViewAnimationOptionBeginFromCurrentState animations:^{
            self.previewContainer.frame = self.previewContainerFrameShown; 
        } completion:^(BOOL finished) {
            
        }];
        [UIView animateWithDuration:.25 animations:^{
        }];
    }
}

- (void)mapView:(MKMapView *)mapView didDeselectAnnotationView:(MKAnnotationView *)view {
    //STEntityAnnotation* annotation = (id)view.annotation;
    [UIView animateWithDuration:.25 delay:0 options:UIViewAnimationOptionBeginFromCurrentState animations:^{
        self.previewContainer.frame = self.previewContainerFrameHidden;
    } completion:^(BOOL finished) {
        
    }];
}

- (MKOverlayView*)mapView:(MKMapView *)mapView viewForOverlay:(id<MKOverlay>)overlay {
    NSLog(@"getting View");
    if (![overlay isKindOfClass:[STConsumptionMapTile class]]) {
        return nil;
    }
    else {
        NSLog(@"adfs");
        return [[[STConsumptionMapTileView alloc] initWithMapTile:(id)overlay] autorelease];
    }
}

- (void)update {
    NSString* key = [STConsumptionMapCache keyForSubcategory:self.subcategory
                                                       scope:self.scope 
                                                      filter:self.filter 
                                                       query:self.query];
    STConsumptionMapCache* cache = [self.caches objectForKey:key];
    if (!cache) {
        cache = [[[STConsumptionMapCache alloc] initWithSubcategory:self.subcategory scope:self.scope filter:self.filter query:self.query] autorelease];
        [self.caches setObject:cache forKey:key];
    }
    for (STConsumptionMapTile* tile in self.tileOverlays) {
        [self.mapView removeOverlay:tile];
    }
    [self.tileOverlays removeAllObjects];
    
    if ([STConfiguration flag:_cacheOverlayKey]) {
        NSArray* cachedTiles = [cache cachedTilesForRegion:self.mapView.region];
        [self.tileOverlays addObjectsFromArray:cachedTiles];
        [self.mapView addOverlays:self.tileOverlays];
    }
    for (STCancellation* c in self.cancellations) {
        [c cancel];
    }
    [self.cancellations removeAllObjects];
    STCancellation* cancellation = [cache entitiesForRegion:self.mapView.region
                                                andCallback:^(NSArray<STEntityDetail> *entities, NSError *error, STCancellation *cancellation2) {
                                                    [self.cancellations removeObject:cancellation2];
                                                    NSMutableDictionary* doomed = [NSMutableDictionary dictionary];
                                                    for (STEntityAnnotation* annotation in self.annotations) {
                                                        [doomed setObject:annotation forKey:annotation.entityDetail.entityID];
                                                    }
                                                    [self.annotations removeAllObjects];
                                                    for (id<STEntityDetail> entity in entities) {
                                                        NSString* entityID = entity.entityID;
                                                        STEntityAnnotation* annotation = [doomed objectForKey:entityID];
                                                        if (annotation) {
                                                            [doomed removeObjectForKey:entityID];
                                                        }
                                                        else {
                                                            annotation = [[[STEntityAnnotation alloc] initWithEntityDetail:entity] autorelease];
                                                            [self.mapView addAnnotation:annotation];
                                                        }
                                                        [self.annotations addObject:annotation];
                                                    }
                                                    for (STEntityAnnotation* annotation in doomed.allValues) {
                                                        [self.mapView removeAnnotation:annotation];
                                                    }
                                                }];
    [self.cancellations addObject:cancellation];
}


#pragma mark - STSliderScopeViewDelegate

- (void)sliderScopeView:(STSliderScopeView*)slider didChangeScope:(STStampedAPIScope)scope {
    self.scope = scope;
}


#pragma mark - UITextFieldDelegate Methods.

- (BOOL)textField:(UITextField *)textField shouldChangeCharactersInRange:(NSRange)range replacementString:(NSString *)string {
    [Util executeOnMainThread:^{
        self.query = [textField.text isEqualToString:@""] ? nil : textField.text;
    }];
    return YES;
}

- (void)textFieldDidBeginEditing:(UITextField*)textField {
    //Override collapsing behavior
}

- (void)textFieldDidEndEditing:(UITextField *)textField {
    //Override collapsing behavior
    self.query = [textField.text isEqualToString:@""] ? nil : textField.text;
}

- (BOOL)textFieldShouldReturn:(UITextField*)textField {
    [textField resignFirstResponder];
    return YES;
}

#pragma mark - Slice mutations

- (void)setQuery:(NSString *)query {
    if (query != query_ && ![query isEqualToString:query_]) {
        [query_ autorelease];
        query_ = [query copy];
        [self update];
    }
}

- (void)setScope:(STStampedAPIScope)scope {
    if (scope_ != scope) {
        scope_ = scope;
        [self update];
    }
}

- (void)toolbar:(STConsumptionToolbar *)toolbar didMoveToItem:(STConsumptionToolbarItem *)item from:(STConsumptionToolbarItem *)previous {
    if ([item.type isEqualToString:_subcategoryType]) {
        self.filter = nil;
        self.subcategory = item.value;
    }
    else if ([item.type isEqualToString:_filterType]) {
        self.filter = item.value;
        self.subcategory = item.parent.value;
    }
    else {
        self.filter = nil;
        self.subcategory = nil;
    }
    [self update];
}

#pragma mark - Configuration

+ (void)setupConfigurations {
    [STConfiguration addFlag:NO forKey:_cacheOverlayKey];
    
    [STConfiguration addString:@"Restaurants" forKey:_restaurantNameKey];
    [STConfiguration addString:@"cat_icon_eDetail_food" forKey:_restaurantIconKey];
    [STConfiguration addString:@"cat_icon_eDetail_food" forKey:_restaurantBackIconKey];
    
    [STConfiguration addString:@"Bars" forKey:_barNameKey];
    [STConfiguration addString:@"cat_icon_eDetail_food" forKey:_barIconKey];
    [STConfiguration addString:@"cat_icon_eDetail_food" forKey:_barBackIconKey];
    
    [STConfiguration addString:@"Cafes" forKey:_cafeNameKey];
    [STConfiguration addString:@"cat_icon_eDetail_food" forKey:_cafeIconKey];
    [STConfiguration addString:@"cat_icon_eDetail_food" forKey:_cafeBackIconKey];
}

@end


@implementation STConsumptionMapCache

@synthesize key = key_;
@synthesize scope = scope_;
@synthesize subcategory = subcategory_;
@synthesize filter = filter_;
@synthesize query = query_;
@synthesize cache = cache_;

- (id)initWithSubcategory:(NSString*)subcategory 
                    scope:(STStampedAPIScope)scope 
                   filter:(NSString*)filter 
                    query:(NSString*)query {
    self = [super init];
    if (self) {
        subcategory_ = [subcategory retain];
        scope_ = scope;
        filter_ = [filter retain];
        query_ = [query retain];
        cache_ = [[NSCache alloc] init];
    }
    return self;
}

- (void)handleResponseWithEntities:(NSArray<STEntityDetail>*)entities
                             error:(NSError*)error 
                      cancellation:(STCancellation*)cancellation 
                             frame:(STTileRect)frame
                       andCallback:(void (^)(NSArray<STEntityDetail>*, NSError*, STCancellation*))block {
    if (entities) {
        for (NSInteger x = frame.x; x < frame.x + frame.width; x++) {
            for (NSInteger y = frame.y; y < frame.y + frame.height; y++) {
                NSString* tileKey = [STConsumptionMapTile keyForX:x y:y andZoom:frame.zoom];
                STConsumptionMapTile* tile = [self.cache objectForKey:tileKey];
                if (!tile) {
                    tile = [[[STConsumptionMapTile alloc] initWithX:x y:y andZoom:frame.zoom] autorelease];
                    [self.cache setObject:tile forKey:tileKey];
                    // NSLog(@"created cache tile:%@",tileKey);
                }
            }
        }
        for (id<STEntityDetail> entity in entities) {
            NSArray* coordinates = [entity.coordinates componentsSeparatedByString:@","];
            CGFloat latitude = [(NSString*)[coordinates objectAtIndex:0] floatValue];
            CGFloat longitude = [(NSString*)[coordinates objectAtIndex:1] floatValue];
            CGPoint lonLat =CGPointMake(longitude, latitude);
            STTileRect origin = [STConsumptionMapViewController tileOriginWithPoint:lonLat andZoom:frame.zoom];
            NSString* tileKey = [STConsumptionMapTile keyForX:origin.x y:origin.y andZoom:frame.zoom];
            STConsumptionMapTile* tile = [self.cache objectForKey:tileKey];
            if (!tile) {
                tile = [[[STConsumptionMapTile alloc] initWithX:origin.x y:origin.y andZoom:frame.zoom] autorelease];
                [self.cache setObject:tile forKey:tileKey];
            }
            [tile.entities setObject:entity forKey:entity.entityID];
        }
    }
    block(entities, error, cancellation);
}

- (NSArray*)cachedTilesForRegion:(MKCoordinateRegion)region {
    STTileRect frame = [STConsumptionMapViewController tileFrameWithRegion:region];
    NSSet* tileKeys = [STConsumptionMapViewController tileKeysForTileFrame:frame];
    NSMutableArray* tiles = [NSMutableArray array];
    for (NSString* tileKey in tileKeys) {
        STConsumptionMapTile* tile = [self.cache objectForKey:tileKey];
        if (tile) {
            [tiles addObject:tile];
        }
    }
    return tiles;
}

- (STCancellation*)entitiesForRegion:(MKCoordinateRegion)region
                         andCallback:(void (^)(NSArray<STEntityDetail>*, NSError* error, STCancellation* cancellation))block {
    STTileRect frame = [STConsumptionMapViewController tileFrameWithRegion:region];
    NSSet* tileKeys = [STConsumptionMapViewController tileKeysForTileFrame:frame];
    NSMutableArray* tiles = [NSMutableArray array];
    for (NSString* tileKey in tileKeys) {
        STConsumptionMapTile* tile = [self.cache objectForKey:tileKey];
        if (tile) {
            //NSLog(@"found cache tile:%@", tileKey);
            [tiles addObject:tile];
        }
        else {
            //NSLog(@"missed cache tile:%@", tileKey);
        }
    }
    if (tileKeys.count == tiles.count) {
        NSLog(@"\n\n\nServing from Cache\n\n\n");
        NSMutableArray<STEntityDetail>* entities = [NSMutableArray array];
        for (STConsumptionMapTile* tile in tiles) {
            [entities addObjectsFromArray:tile.entities.allValues];
        }
        STCancellation* cancellation = [STCancellation cancellation];
        [Util executeOnMainThread:^{
            if (!cancellation.cancelled) {
                block(entities, nil, cancellation);
            }
        }];
        return cancellation;
    }
    else {
        //Expand region for better caching
        region.span.latitudeDelta *= 1.4;
        region.span.longitudeDelta *= 1.4;
        frame = [STConsumptionMapViewController tileFrameWithRegion:region withZoom:frame.zoom];
        CGRect actualFrame = [STConsumptionMapViewController coordinateFrame:frame];
        NSInteger tileCount = frame.width * frame.height;
        STConsumptionSlice* slice = [[[STConsumptionSlice alloc] init] autorelease];
        slice.offset = [NSNumber numberWithInteger:0];
        slice.limit = [NSNumber numberWithInteger:tileCount*1.5];
        slice.category = @"food";
        NSString* scope = @"you";
        if (self.scope == STStampedAPIScopeYou) {
            scope = @"me";
        }
        else if (self.scope == STStampedAPIScopeFriends) {
            scope = @"inbox";
        }
        else if (self.scope == STStampedAPIScopeEveryone) {
            scope = @"everyone";
        }
        slice.scope = scope;
        //slice.subcategory = self.subcategory;
        slice.filter = self.filter;
        slice.query = self.query;
        if (slice.query) {
            slice.sort = @"relevance";
        }
        slice.viewport = [NSString stringWithFormat:@"%f,%f,%f,%f", 
                          actualFrame.origin.y + actualFrame.size.height,
                          actualFrame.origin.x,
                          actualFrame.origin.y,
                          actualFrame.origin.x + actualFrame.size.width];
        return [[STStampedAPI sharedInstance] entitiesForConsumptionSlice:slice 
                                                              andCallback:^(NSArray<STEntityDetail> *entities, NSError *error, STCancellation *cancellation) {
                                                                  [self handleResponseWithEntities:entities error:error cancellation:cancellation frame:frame andCallback:block];
                                                              }];
    }
}

+ (NSString*)keyForSubcategory:(NSString*)subcategory 
                         scope:(STStampedAPIScope)scope 
                        filter:(NSString*)filter
                         query:(NSString*)query {
    return [NSString stringWithFormat:@"%@,%d,%@,%@", subcategory, scope, filter, query];
}

+ (void)componentsForKey:(NSString*)key 
             subcategory:(NSString**)subcategory 
                   scope:(STStampedAPIScope*)scope 
                  filter:(NSString**)filter 
                   query:(NSString**)query {
    NSArray* comps = [key componentsSeparatedByString:@","];
    if (comps.count == 4) {
        *subcategory = [comps objectAtIndex:0];
        *scope = [[comps objectAtIndex:1] integerValue];
        *filter = [comps objectAtIndex:2];
        *query = [comps objectAtIndex:3];
    }
}

@end

@implementation STConsumptionMapTile

@synthesize x = x_;
@synthesize y = y_;
@synthesize zoom = zoom_;
@synthesize entities = _entities;
@synthesize key = key_;

- (id)initWithX:(NSInteger)x y:(NSInteger)y andZoom:(NSInteger)zoom
{
    self = [super init];
    if (self) {
        x_ = x;
        y_ = y;
        zoom_ = zoom;
        _entities = [[NSMutableDictionary alloc] init];
        key_ = [[STConsumptionMapTile keyForX:x_ y:y_ andZoom:zoom_] retain];
    }
    return self;
}

- (id)initWithCoder:(NSCoder *)decoder {
    self = [super init];
    if (self) {
        x_ = [decoder decodeIntegerForKey:@"x"];
        y_ = [decoder decodeIntegerForKey:@"y"];
        zoom_ = [decoder decodeIntegerForKey:@"zoom"];
        _entities = [[decoder decodeObjectForKey:@"entities"] retain];
        key_ = [[decoder decodeObjectForKey:@"key"] retain];
    }
    return self;
}

- (void)dealloc
{
    [_entities release];
    [key_ release];
    [super dealloc];
}

- (void)encodeWithCoder:(NSCoder *)encoder {
    [encoder encodeInteger:self.x forKey:@"x"];
    [encoder encodeInteger:self.y forKey:@"y"];
    [encoder encodeInteger:self.zoom forKey:@"zoom"];
    [encoder encodeObject:self.entities forKey:@"entities"];
    [encoder encodeObject:self.key forKey:@"key"];
}

+ (NSString*)keyForX:(NSInteger)x y:(NSInteger)y andZoom:(NSInteger)zoom {
    return [NSString stringWithFormat:@"%d,%d,%d", x, y, zoom];
}

- (CLLocationCoordinate2D)coordinate {
    CGFloat tileSize = [STConsumptionMapViewController tileSizeWithZoomLevel:self.zoom];
    CLLocationCoordinate2D origin;
    origin.longitude = self.x * tileSize + tileSize / 2.0;
    origin.latitude = self.y * tileSize + tileSize / 2.0;
    return origin;
}

- (MKMapRect)boundingMapRect {
    CGFloat tileSize = [STConsumptionMapViewController tileSizeWithZoomLevel:self.zoom];
    CGFloat half = tileSize / 2.0;
    CLLocationCoordinate2D center = self.coordinate;
    
    CLLocationCoordinate2D topLeftCoordinate;
    topLeftCoordinate.latitude = center.latitude + half;
    topLeftCoordinate.longitude = center.longitude - half;
    
    MKMapPoint topLeft = MKMapPointForCoordinate(topLeftCoordinate);
    
    CLLocationCoordinate2D bottomRightCoord;
    bottomRightCoord.latitude = center.latitude - half;
    bottomRightCoord.longitude = center.longitude + half;
    
    MKMapPoint bottomRight = MKMapPointForCoordinate(bottomRightCoord);
    
    double width = bottomRight.x - topLeft.x;
    double height = bottomRight.y - topLeft.y;
    
    MKMapRect bounds = MKMapRectMake(topLeft.x, topLeft.y, width, height);
    return bounds;
}

@end

@implementation STConsumptionMapTileView

@synthesize tile = tile_;

- (id)initWithMapTile:(STConsumptionMapTile*)tile {
    self = [super initWithOverlay:tile];
    if (self) {
        tile_ = [tile retain];
    }
    return self;
}

- (void)dealloc
{
    [tile_ release];
    [super dealloc];
}

- (void)drawMapRect:(MKMapRect)mapRect
          zoomScale:(MKZoomScale)zoomScale
          inContext:(CGContextRef)ctx
{
    CGContextSetAlpha(ctx, 0.5);
    MKMapRect boundary = self.tile.boundingMapRect;
    
    //NSLog(@"drawing:%f,%f,%f,%f", boundary.origin.x, boundary.origin.y, boundary.size.width, boundary.size.height);
    CGContextSetFillColorWithColor(ctx, [UIColor redColor].CGColor);
    CGContextSetStrokeColorWithColor(ctx, [UIColor blackColor].CGColor);
    // Convert the MKMapRect (absolute points on the map proportional to screen points) to
    // a CGRect (points relative to the origin of this view) that can be drawn.
    CGRect boundaryCGRect = [self rectForMapRect:boundary];
    
    CGContextFillRect(ctx, boundaryCGRect);
    CGContextStrokeRect(ctx, boundaryCGRect);
    
}

@end
