//
//  EditEntityViewController.h
//  Stamped
//
//  Created by Andrew Bonventre on 8/27/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

@interface EditEntityViewController : UIViewController

@property (nonatomic, retain) IBOutlet UIImageView* categoryDropdownImageView;

- (IBAction)categoryDropdownPressed:(id)sender;
@end
