//
//  STSegmentedControl.h
//  Stamped
//
//  Created by Devin Doty on 6/18/12.
//
//

#import <UIKit/UIKit.h>

@interface STSegmentedControl : UIControl

- (id)initWithItems:(NSArray *)items; // items can be NSStrings. control is automatically sized to fit content

@property(nonatomic,retain) NSArray *items;
@property(nonatomic,assign) NSInteger selectedSegmentIndex;


@end
