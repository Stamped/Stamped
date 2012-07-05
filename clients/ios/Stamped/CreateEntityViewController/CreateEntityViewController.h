//
//  CreateEntityViewController.h
//  Stamped
//
//  Created by Devin Doty on 6/18/12.
//
//

#import <UIKit/UIKit.h>


@protocol CreateEntityViewControllerDelegate;
@interface CreateEntityViewController : UITableViewController

- (id)initWithEntityCategory:(NSString*)category entityTitle:(NSString *)title;

@property(nonatomic,assign) id <CreateEntityViewControllerDelegate> delegate;

@end
@protocol CreateEntityViewControllerDelegate

@end