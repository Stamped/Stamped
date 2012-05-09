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
#import "STPlaceAnnotation.h"
#import "STConfiguration.h"
#import <math.h>
#import "Util.h"

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

@interface STConsumptionMapTile : NSObject

- (id)initWithX:(NSInteger)x y:(NSInteger)y andZoom:(NSInteger)zoom;

+ (NSString*)keyForX:(NSInteger)x y:(NSInteger)y andZoom:(NSInteger)zoom;

@property (nonatomic, readonly, assign) NSInteger x;
@property (nonatomic, readonly, assign) NSInteger y;
@property (nonatomic, readonly, assign) NSInteger zoom;
@property (nonatomic, readonly, retain) NSMutableDictionary* stamps;
@property (nonatomic, readonly, copy) NSString* key;

@end

@interface STConsumptionAnnotation : NSObject <MKAnnotation>

- (id)initWithStamp:(id<STStamp>)stamp;

@property (nonatomic, readonly, retain) id<STStamp> stamp;

@end

@interface STConsumptionMapCache : NSObject

- (id)initWithSubcategory:(NSString*)subcategory 
                    scope:(STStampedAPIScope)scope 
                   filter:(NSString*)filter 
                    query:(NSString*)query;

- (STCancellation*)stampsForRegion:(MKCoordinateRegion)region
                       andCallback:(void (^)(NSArray<STStamp>* stamps, NSError* error, STCancellation* cancellation))block;

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

@interface STConsumptionMapViewController () <MKMapViewDelegate>

- (void)update;

@property (nonatomic, readonly, retain) STConsumptionToolbar* consumptionToolbar;
@property (nonatomic, readonly, retain) STSearchField* searchField;
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
@property (nonatomic, readwrite, assign) BOOL cachingDisabled;

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
  }
  return self;
}

- (void)dealloc
{
  [caches_ release];
  [consumptionToolbar_ release];
  [subcategory_ release];
  [filter_ release];
  [query_ release];
  [super dealloc];
}

- (void)viewDidLoad
{
  [super viewDidLoad];
  self.zoomToUserLocation = YES;
  UIView* searchBar = [[[UIView alloc] initWithFrame:CGRectMake(0, 0, 320, 40)] autorelease];
  searchField_ = [[STSearchField alloc] initWithFrame:CGRectMake(10, 5, 300, 30)];
  searchField_.placeholder = @"Search for stamps";
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
  mapView_.delegate = self;
  [self update];
}

- (void)viewDidAppear:(BOOL)animated {
  mapView_.showsUserLocation = YES;
}

- (void)viewDidUnload
{
  [super viewDidUnload];
  // Release any retained subviews of the main view.
  [searchField_ release];
  searchField_ = nil;
  [mapView_ release];
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
  CGFloat tileHeight = 3;
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
  NSLog(@"tile size: %f", tileSize);
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
  tileRect.width = ceil( region.span.longitudeDelta / tileSize );
  tileRect.height = ceil( region.span.latitudeDelta / tileSize );
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
  CGFloat originDelta = MKMetersBetweenMapPoints(lastMapRect_.origin, mapView.visibleMapRect.origin);
  MKMapPoint upperRight = MKMapPointMake(MKMapRectGetMaxX(lastMapRect_), MKMapRectGetMinY(lastMapRect_));
  CGFloat span = MKMetersBetweenMapPoints(lastMapRect_.origin, upperRight);
  
  //NSLog(@"%d",[self zoomLevel]);
  //if ((originDelta / span) < kMapSpanHysteresisPercentage)
  //return;
  
  //if (searchField_.text.length > 0)
  //return;
  lastMapRect_ = mapView.visibleMapRect;
  MKCoordinateRegion region = self.mapView.region;
  //NSLog(@"%f,%f,%f,%f",region.center.latitude, region.center.longitude, region.span.latitudeDelta, region.span.longitudeDelta);
  
  //CGRect frame = [self tileFrame];
  ///NSLog(@"frame:%f,%f,%f,%f", frame.origin.x, frame.origin.y, frame.size.width, frame.size.height);
  //[self resetCaches];
  //[self loadDataFromNetwork];
  [self update]; 
}

- (MKAnnotationView*)mapView:(MKMapView*)theMapView viewForAnnotation:(id<MKAnnotation>)annotation {
  return [[[MKPinAnnotationView alloc] initWithAnnotation:annotation reuseIdentifier:@"TODO"] autorelease];
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
  for (STCancellation* c in self.cancellations) {
    [c cancel];
  }
  STCancellation* cancellation = [cache stampsForRegion:self.mapView.region
                                            andCallback:^(NSArray<STStamp> *stamps, NSError *error, STCancellation *cancellation2) {
                                              [self.cancellations removeObject:cancellation2];
                                              [self.mapView removeAnnotations:self.annotations];
                                              [self.annotations removeAllObjects];
                                              for (id<STStamp> stamp in stamps) {
                                                STConsumptionAnnotation* annotation = [[[STConsumptionAnnotation alloc] initWithStamp:stamp] autorelease];
                                                [self.annotations addObject:annotation];
                                                [self.mapView addAnnotation:annotation];
                                              }
                                            }];
  [self.cancellations addObject:cancellation];
}

+ (void)setupConfigurations {
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

- (void)handleResponseWithStamps:(NSArray<STStamp>*)stamps 
                           error:(NSError*)error 
                    cancellation:(STCancellation*)cancellation 
                           frame:(STTileRect)frame
                     andCallback:(void (^)(NSArray<STStamp>*, NSError*, STCancellation*))block {
  if (stamps) {
    for (NSInteger x = frame.x; x < frame.x + frame.width; x++) {
      for (NSInteger y = frame.y; y < frame.y + frame.height; y++) {
        NSString* tileKey = [STConsumptionMapTile keyForX:x y:y andZoom:frame.zoom];
        STConsumptionMapTile* tile = [self.cache objectForKey:tileKey];
        if (!tile) {
          tile = [[[STConsumptionMapTile alloc] initWithX:x y:y andZoom:frame.zoom] autorelease];
          [self.cache setObject:tile forKey:tileKey];
          NSLog(@"created cache tile:%@",tileKey);
        }
      }
    }
    for (id<STStamp> stamp in stamps) {
      NSArray* coordinates = [stamp.entity.coordinates componentsSeparatedByString:@","];
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
      [tile.stamps setObject:stamp forKey:stamp.stampID];
    }
  }
  block(stamps, error, cancellation);
}

- (STCancellation*)stampsForRegion:(MKCoordinateRegion)region
                       andCallback:(void (^)(NSArray<STStamp>* stamps, NSError* error, STCancellation* cancellation))block {
  STTileRect frame = [STConsumptionMapViewController tileFrameWithRegion:region];
  NSSet* tileKeys = [STConsumptionMapViewController tileKeysForTileFrame:frame];
  NSMutableArray* tiles = [NSMutableArray array];
  for (NSString* tileKey in tileKeys) {
    STConsumptionMapTile* tile = [self.cache objectForKey:tileKey];
    if (tile) {
      NSLog(@"found cache tile:%@", tileKey);
      [tiles addObject:tile];
    }
    else {
      NSLog(@"missed cache tile:%@", tileKey);
    }
  }
  if (tileKeys.count == tiles.count) {
    NSLog(@"\n\n\nServing from Cache\n\n\n");
    NSMutableArray<STStamp>* stamps = [NSMutableArray array];
    for (STConsumptionMapTile* tile in tiles) {
      [stamps addObjectsFromArray:tile.stamps.allValues];
    }
    STCancellation* cancellation = [STCancellation cancellation];
    [Util executeOnMainThread:^{
      if (!cancellation.cancelled) {
        block(stamps, nil, cancellation);
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
    slice.scope = [[STStampedAPI sharedInstance] stringForScope:self.scope];
    slice.subcategory = self.subcategory;
    slice.filter = self.filter;
    slice.viewport = [NSString stringWithFormat:@"%f,%f,%f,%f", 
                      actualFrame.origin.y + actualFrame.size.height,
                      actualFrame.origin.x,
                      actualFrame.origin.y,
                      actualFrame.origin.x + actualFrame.size.width];
    return [[STStampedAPI sharedInstance] stampsForConsumptionSlice:slice 
                                                        andCallback:^(NSArray<STStamp> *stamps, NSError *error, STCancellation *cancellation) {
                                                          [self handleResponseWithStamps:stamps error:error cancellation:cancellation frame:frame andCallback:block];
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
@synthesize stamps = stamps_;
@synthesize key = key_;

- (id)initWithX:(NSInteger)x y:(NSInteger)y andZoom:(NSInteger)zoom
{
  self = [super init];
  if (self) {
    x_ = x;
    y_ = y;
    zoom_ = zoom;
    stamps_ = [[NSMutableDictionary alloc] init];
    key_ = [STConsumptionMapTile keyForX:x_ y:y_ andZoom:zoom_];
  }
  return self;
}

+ (NSString*)keyForX:(NSInteger)x y:(NSInteger)y andZoom:(NSInteger)zoom {
  return [NSString stringWithFormat:@"%d,%d,%d", x, y, zoom];
}

@end

@implementation STConsumptionAnnotation

@synthesize stamp = stamp_;
@synthesize coordinate = coordinate_;

- (id)initWithStamp:(id<STStamp>)stamp {
  self = [super init];
  if (self) {
    
    NSArray* coordinates = [stamp.entity.coordinates componentsSeparatedByString:@","];
    CGFloat latitude = [(NSString*)[coordinates objectAtIndex:0] floatValue];
    CGFloat longitude = [(NSString*)[coordinates objectAtIndex:1] floatValue];
    coordinate_ = CLLocationCoordinate2DMake(latitude, longitude);
  }
  return self;
}

- (void)dealloc
{
  [stamp_ release];
  [super dealloc];
}

- (NSString *)title {
  return self.stamp.entity.title;
}

- (NSString *)subtitle {
  if (stamp_) {
    if (stamp_.via.length > 0)
      return stamp_.via;
    
    return [NSString stringWithFormat:@"@%@", stamp_.user.screenName];
  }
  return self.stamp.entity.subtitle;
}

@end
