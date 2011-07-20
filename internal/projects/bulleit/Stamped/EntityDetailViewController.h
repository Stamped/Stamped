//
//  EntityDetailViewController.h
//  Stamped
//
//  Created by Andrew Bonventre on 7/9/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

@class Stamp;

@interface EntityDetailViewController : UIViewController {
 @protected
  Stamp* stamp_;
}

- (id)initWithNibName:(NSString*)nibNameOrNil stamp:(Stamp*)stamp;

@property (nonatomic, retain) IBOutlet UIScrollView* scrollView;
@property (nonatomic, retain) IBOutlet UILabel* titleLabel;
@property (nonatomic, retain) IBOutlet UILabel* descriptionLabel;
@property (nonatomic, retain) IBOutlet UIButton* mainActionButton;
@property (nonatomic, retain) IBOutlet UILabel* mainActionLabel;

@end
