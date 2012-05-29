//
//  EntityViewController.m
//  Stamped
//
//  Created by Devin Doty on 5/28/12.
//
//

#import "EntityViewController.h"
#import "EntityHeaderView.h"
#import "STPhotoViewController.h"

@interface EntityViewController ()

@end

@implementation EntityViewController

- (id)init {
    if (self = [super init]) {
    }
    return self;
}

- (void)viewDidLoad {
    [super viewDidLoad];
}

- (void)viewDidUnload {
    [super viewDidUnload];
    
    if (!self.tableView.tableHeaderView) {
        
        EntityHeaderView *view = [[EntityHeaderView alloc] initWithFrame:CGRectMake(0.0f, 0.0f, self.view.bounds.size.width, 200.0f)];
        view.delegate = (id<EntityHeaderViewDelegate>)self;
        view.autoresizingMask = UIViewAutoresizingFlexibleWidth;
        self.tableView.tableHeaderView = view;
        [view release];
        
    }
    
    
}


#pragma mark - UITableViewDataSource

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {

    return 0;
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
    
    
    return nil;
}



#pragma mark - UITableViewDelegate


#pragma mark - EntityHeaderViewDelegate

- (void)entityHeaderView:(EntityHeaderView*)view imageViewTapped:(UIImageView*)imageView {
    
}

- (void)entityHeaderView:(EntityHeaderView*)view mapViewTapped:(MKMapView*)mapView {
    
   // UIActionSheet *actionSheet = [[UIActionSheet alloc] init
    
}

@end
