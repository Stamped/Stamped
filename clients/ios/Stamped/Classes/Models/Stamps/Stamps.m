//
//  Stamps.m
//  Stamped
//
//  Created by Devin Doty on 5/18/12.
//
//

#import "Stamps.h"
#import "STConfiguration.h"

NSString* const StampsChangedNotification = @"StampsChangedNotification";
static const CGFloat _maxAge = 60;

@interface StampsScopeState : NSObject <NSCoding>

- (id)initWithOldState:(StampsScopeState*)state;

- (NSString*)objectAtIndex:(NSInteger)index;
- (NSInteger)count;

@property (nonatomic, readonly, retain) NSDate* date;
@property (nonatomic, readonly, retain) NSMutableArray* currentIDs;
@property (nonatomic, readonly, retain) NSMutableArray* oldIDs;
@property (nonatomic, readonly, assign) NSInteger required;

@end

@implementation StampsScopeState

@synthesize date = date_;
@synthesize currentIDs = currentIDs_;
@synthesize oldIDs = oldIDs_;
@synthesize required = required_;

- (id)init {
  self = [super init];
  if (self) {
    date_ = [[NSDate date] retain];
    currentIDs_ = [[NSMutableArray alloc] init];
    oldIDs_ = [[NSMutableArray alloc] init];
    required_ = 20;
  }
  return self;
}

- (id)initWithOldState:(StampsScopeState*)state {
  self = [self init];
  if (self && state) {
    for (NSInteger i = state.currentIDs.count - 1; i >= 0; i++) {
      NSString* stampID = [state.currentIDs objectAtIndex:i];
      [self.oldIDs addObject:stampID];
    }
  }
  return self;
}

- (id)initWithCoder:(NSCoder *)decoder {
  self = [super init];
  if (self) {
    date_ = [[decoder decodeObjectForKey:@"date"] retain];
    currentIDs_ = [[decoder decodeObjectForKey:@"currentIDs"] retain];
    oldIDs_ = [[decoder decodeObjectForKey:@"oldIDs"] retain];
    required_ = [decoder decodeIntegerForKey:@"required"];
  }
  return self;
}

- (void)dealloc
{
  [date_ release];
  [currentIDs_ release];
  [oldIDs_ release];
  [super dealloc];
}

- (void)encodeWithCoder:(NSCoder *)encoder {
  [encoder encodeObject:self.date forKey:@"date"];
  [encoder encodeObject:self.currentIDs forKey:@"currentIDs"];
  [encoder encodeObject:self.oldIDs forKey:@"oldIDs"];
  [encoder encodeInteger:self.required forKey:@"required"];
}

- (NSInteger)count {
  return self.currentIDs.count + self.oldIDs.count;
}

- (NSString *)objectAtIndex:(NSInteger)index {
  NSInteger curCount = self.currentIDs.count;
  if (index > curCount) {
    return [self.oldIDs objectAtIndex:(self.oldIDs.count - (index - curCount + 1))];
  }
  else {
    return [self.currentIDs objectAtIndex:index];
  }
}

- (void)addStamp:(id<STStamp>)stamp {
  [self.currentIDs addObject:stamp.stampID];
  //TODO
}

@end

@interface Stamps ()

- (void)updateSlice;

@property (nonatomic, readonly, retain) NSMutableDictionary* data;
@property (nonatomic, readwrite, assign) BOOL reloading;
@property (nonatomic, readwrite, assign) BOOL moreData;

@end

@implementation Stamps

@synthesize reloading = _reloading;
@synthesize moreData = _moreData;
@synthesize scope = _scope;
@synthesize searchQuery = _searchQuery;
@synthesize data = _data;

static id _sharedInstance;

+ (void)initialize {
  _sharedInstance = [[Stamps alloc] init];
}

+ (Stamps*)sharedInstance {
  return _sharedInstance;
}

- (id)init {
  self = [super init];
  if (self) {
    _data = [[NSMutableDictionary alloc] init];
    _moreData = YES;
    _reloading = NO;
    _scope = STStampedAPIScopeFriends;
    _searchQuery = nil;
  }
  return self;
}

- (void)dealloc {
  [self cancel];
  [_data release];
  _data=nil;
  [_searchQuery release];
  _searchQuery = nil;
  [super dealloc];
}

- (id)keyForScope:(STStampedAPIScope)scope {
  return [NSNumber numberWithInteger:scope];
}

- (StampsScopeState*)stateForScope:(STStampedAPIScope)scope {
  StampsScopeState* state = [self.data objectForKey:[self keyForScope:scope]];
  if (!state) {
    state = [[[StampsScopeState alloc] init] autorelease];
    [self.data setObject:state forKey:[self keyForScope:scope]];
  }
  else if ([state.date timeIntervalSinceNow] > _maxAge) {
    state = [[[StampsScopeState alloc] initWithOldState:state] autorelease];
    [self.data setObject:state forKey:[self keyForScope:scope]];
  }
  return state;
}


#pragma mark - Stamps Loading

- (void)loadMore {
  StampsScopeState* state = [self stateForScope:self.scope];
  
  STGenericCollectionSlice *slice = nil;
  
  switch (_scope) {
    case STStampedAPIScopeYou: {
      STUserCollectionSlice *tempSlice = [[[STUserCollectionSlice alloc] init] autorelease];
      tempSlice.userID = [[STStampedAPI sharedInstance].currentUser userID];
      slice = tempSlice;
    }
      break;
    case STStampedAPIScopeFriends: {
      STGenericCollectionSlice* tempSlice = [[[STGenericCollectionSlice alloc] init] autorelease];
      slice = tempSlice;
    }
      break;
    case STStampedAPIScopeFriendsOfFriends: {
      STFriendsSlice *tempSlice = [[[STFriendsSlice alloc] init] autorelease];
      tempSlice.distance = [NSNumber numberWithInteger:2];
      tempSlice.inclusive = [NSNumber numberWithBool:NO];
      slice = tempSlice;
    }
      break;            
    default: {
      STGenericCollectionSlice* tempSlice = [[[STGenericCollectionSlice alloc] init] autorelease];
      slice = tempSlice;
    }
      break;
  }
  if (_searchQuery != nil && ![_searchQuery isEqualToString:@""]) {
    slice.query = _searchQuery;
  }
  else {
    slice.query = nil;
  }
  slice.sort = @"stamped";
  slice.before = [NSDate date];
  slice.limit = [NSNumber numberWithInt:20];
  
  [[STStampedAPI sharedInstance] stampsForInboxSlice:slice andCallback:^(NSArray<STStamp>* stamps, NSError* error, STCancellation* cancellation){
    NSLog(@"finished : %@", [stamps description]);
    _reloading = NO;
    _moreData = NO;
    for (id<STStamp> stamp in stamps) {
      [self.data addObject:stamp.stampID];
    }
    [[NSNotificationCenter defaultCenter] postNotification:[NSNotification notificationWithName:StampsChangedNotification object:nil]];
  }];
}

- (void)reloadData {
  if (_reloading) return;
  _reloading = YES;
  
  NSLog(@"RELOADING");  
  StampsScopeState* state = [[[StampsScopeState alloc] initWithOldState:[self stateForScope:self.scope]] autorelease];
  [self.data setObject:state forKey:[self keyForScope:self.scope]];
  
  [self loadMore];
}

- (void)loadNextPage {
  if (_reloading) return;
  _reloading = YES;
  [self loadMore];
}

- (void)cancel {
  NSLog(@"Cancel");
}

#pragma mark - Setters

- (void)setScope:(STStampedAPIScope)scope {
  if (scope != _scope) {
    _scope = scope;
    [self updateSlice];
  }
}

- (void)setSearchQuery:(NSString *)searchQuery {
  [_searchQuery release];
  _searchQuery = [searchQuery retain];
  [self updateSlice];
}

#pragma mark - Stamps Data Source

- (NSString*)stampIDAtIndex:(NSInteger)index {
  return [self.data objectAtIndex:index];
}

- (NSInteger)numberOfStamps {
  return [self.data count];
}

- (BOOL)isEmpty {
  return [self.data count] == 0;
}

- (BOOL)isReloading {
  return _reloading;
}

- (BOOL)hasMoreData {
  return _moreData;
}

@end
