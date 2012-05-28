//
//  EntityViewController.m
//  Stamped
//
//  Created by Devin Doty on 5/28/12.
//
//

#import "EntityViewController.h"

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
}


#pragma mark - UITableViewDataSource

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {

    return 0;
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
    
    
    return nil;
}



#pragma mark - UITableViewDelegate


@end
