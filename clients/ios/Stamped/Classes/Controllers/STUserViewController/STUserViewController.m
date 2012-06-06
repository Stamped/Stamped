//
//  STUserViewController.m
//  Stamped
//
//  Created by Devin Doty on 6/5/12.
//
//

#import "STUserViewController.h"
#import "STUserHeaderView.h"
#import "STSimpleUserDetail.h"

@interface STUserViewController ()
@property(nonatomic,retain) id<STUser> user;
@property(nonatomic,copy) NSString *userIdentifier;
@end

@implementation STUserViewController
@synthesize userIdentifier;
@synthesize user=_user;

- (id)init {
    
    if ((self = [super init])) {
        
        
        
    }
    return self;
    
}

- (id)initWithUserIdentifier:(NSString*)identifier {
    
    if ((self = [super init])) {
        self.userIdentifier = identifier;
    }
    return self;
    
}

- (id)initWithUser:(STSimpleUserDetail*)user {
    
    if (self = [super init]) {
        _user = [user retain];
        self.userIdentifier = user.userID;
        NSLog(@"user id : %@ %@", user.userID, user.identifier);
        
    }
    return self;
    
}

- (void)viewDidLoad {
    [super viewDidLoad];
    
    if (!self.tableView.tableHeaderView) {
        STUserHeaderView *view = [[STUserHeaderView alloc] initWithFrame:CGRectMake(0.0f, 0.0f, self.view.bounds.size.width, 155.0f)];
        view.delegate = (id<STUserHeaderViewDelegate>)self;
        view.autoresizingMask = UIViewAutoresizingFlexibleWidth;
        self.tableView.tableHeaderView = view;
        [view release];
        if (self.user) {
            [view setupWithUser:self.user];
        }
    }
    
    
    [self reloadDataSource];
    
}

- (void)viewDidUnload {
    [super viewDidUnload];
}t

- (void)dealloc {
    [_user release], _user = nil;    
    self.userIdentifier = nil;
    [super dealloc];
}


#pragma mark - Setters

- (void)setUser:(id<STUser>)user {
    [_user release], _user = nil;    
    _user = [user retain];
    
    if (self.tableView.tableHeaderView) {
        STUserHeaderView *view = (STUserHeaderView*)self.tableView.tableHeaderView;
        [view setupWithUser:_user];
    }
    
}


#pragma mark - STUserHeaderViewDelegate

- (void)stUserHeaderView:(STUserHeaderView*)view selectedTab:(STUserHeaderTab)tab {
    
}

- (void)stUserHeaderViewHeightChanged:(STUserHeaderView *)view {
    
}


#pragma mark - UITableViewDataSource

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {
    
    return 0;
    
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
    
    static NSString *CellIdentifier = @"CellIdentifier";
    
    UITableViewCell *cell = [tableView dequeueReusableCellWithIdentifier:CellIdentifier];
    if (cell == nil) {
        cell = [[[UITableViewCell alloc] initWithStyle:UITableViewCellStyleDefault reuseIdentifier:CellIdentifier] autorelease];
    }
    
    
    return cell;
    
}


#pragma mark - STRestController 

- (BOOL)dataSourceReloading {
    return NO;
}

- (void)loadNextPage {
    
}

- (BOOL)dataSourceHasMoreData {
    return NO;
}

- (void)reloadDataSource {
    if (!self.userIdentifier) return; // show failed..
    
    [[STStampedAPI sharedInstance] userDetailForUserID:self.userIdentifier andCallback:^(id<STUserDetail> aUser, NSError *error) {
      
        if (aUser) {
            self.user = aUser;
        }
        
        [self dataSourceDidFinishLoading];

    }];
    
    [super reloadDataSource];
}

- (BOOL)dataSourceIsEmpty {
    return YES;;
}

- (void)setupNoDataView:(NoDataView*)view {
    
    
}

@end
