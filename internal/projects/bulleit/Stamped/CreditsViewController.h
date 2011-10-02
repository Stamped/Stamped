//
//  CreditsViewController.h
//  Stamped
//
//  Created by Andrew Bonventre on 10/1/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>
#import <RestKit/RestKit.h>

@interface CreditsViewController : UIViewController <RKObjectLoaderDelegate,
                                                     UITableViewDelegate,
                                                     UITableViewDataSource>

@property (nonatomic, retain) IBOutlet UITableView* tableView;
@property (nonatomic, copy) NSString* screenName;

@end
