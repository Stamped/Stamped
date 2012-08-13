//
//  CreateEntityViewController.h
//  Stamped
//
//  Created by Devin Doty on 6/18/12.
//
//

/*
 
 The generic controller for creating new entities.
 
 Notes:
 This class is buggy and what's worse, it's the 3rd longest class
 in the project (albeit not that complex). Devin put this together
 as his last contribution and the quality is reflective of that.
 I recommend a thorough audit if not a full rewrite.
 
 2012-08-10
 -Landon 
 */

#import <UIKit/UIKit.h>


@protocol CreateEntityViewControllerDelegate;
@interface CreateEntityViewController : UITableViewController

- (id)initWithEntityCategory:(NSString*)category entityTitle:(NSString *)title;

@property(nonatomic,assign) id <CreateEntityViewControllerDelegate> delegate;

@end
@protocol CreateEntityViewControllerDelegate

@end